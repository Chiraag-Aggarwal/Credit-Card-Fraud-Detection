import hmac
import logging
import os
from contextlib import asynccontextmanager
from time import perf_counter
from typing import Annotated

import pandas as pd
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import Field

from app.model_loader import load_model_artifacts
from app.schemas import PredictionResponse, TransactionFeatures


logger = logging.getLogger("fraud_detection_api")
FEATURE_COLUMNS = ["Time", *[f"V{i}" for i in range(1, 29)], "Amount"]
MAX_BATCH_SIZE = 100


@asynccontextmanager
async def lifespan(application: FastAPI):
    model, threshold, metrics, model_version = load_model_artifacts()
    application.state.model = model
    application.state.threshold = threshold
    application.state.metrics = metrics
    application.state.model_version = model_version
    logger.info("Loaded fraud model version %s", model_version)
    yield


app = FastAPI(title="Fraud Detection ML Service", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-API-Key"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    started = perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("Request failed: %s %s", request.method, request.url.path)
        raise
    logger.info(
        "%s %s returned %s in %.2f ms",
        request.method,
        request.url.path,
        response.status_code,
        (perf_counter() - started) * 1000,
    )
    return response


def verify_api_key(
    api_key: Annotated[str | None, Header(alias="X-API-Key")] = None,
) -> None:
    expected_key = os.getenv("ML_API_KEY")
    if expected_key is not None and (
        api_key is None or not hmac.compare_digest(api_key, expected_key)
    ):
        raise HTTPException(status_code=401, detail="Invalid or missing API key.")


def make_prediction(
    features: TransactionFeatures,
    request: Request,
) -> PredictionResponse:
    row = pd.DataFrame(
        [[getattr(features, column) for column in FEATURE_COLUMNS]],
        columns=FEATURE_COLUMNS,
    )
    probability = float(request.app.state.model.predict_proba(row)[0, 1])
    threshold = request.app.state.threshold
    if probability >= threshold:
        risk_label = "HIGH"
    elif probability >= threshold / 2:
        risk_label = "MEDIUM"
    else:
        risk_label = "LOW"
    return PredictionResponse(
        fraud_probability=probability,
        risk_label=risk_label,
        is_fraud=probability >= threshold,
        threshold=threshold,
        model_version=request.app.state.model_version,
    )


@app.get("/health")
async def health(request: Request) -> dict[str, str | bool]:
    return {
        "status": "model_loaded",
        "model_loaded": hasattr(request.app.state, "model"),
        "model_version": getattr(request.app.state, "model_version", ""),
    }


@app.get("/model-info", dependencies=[Depends(verify_api_key)])
async def model_info(request: Request) -> dict:
    return {**request.app.state.metrics, "threshold": request.app.state.threshold}


@app.post(
    "/predict",
    response_model=PredictionResponse,
    dependencies=[Depends(verify_api_key)],
)
async def predict(
    features: TransactionFeatures,
    request: Request,
) -> PredictionResponse:
    return make_prediction(features, request)


@app.post(
    "/predict/batch",
    response_model=list[PredictionResponse],
    dependencies=[Depends(verify_api_key)],
)
async def predict_batch(
    transactions: Annotated[
        list[TransactionFeatures],
        Field(min_length=1, max_length=MAX_BATCH_SIZE),
    ],
    request: Request,
) -> list[PredictionResponse]:
    return [make_prediction(transaction, request) for transaction in transactions]
