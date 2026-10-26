import json
import os
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from app import model_loader
from app.main import app
from training.train_compare import FEATURE_COLUMNS


def transaction(v1: float = 0.0, amount: float = 10.0) -> dict[str, float]:
    values = {column: 0.0 for column in FEATURE_COLUMNS}
    values["V1"] = v1
    values["Amount"] = amount
    return values


def fit_test_model():
    labels = np.tile([0, 0, 0, 0, 1], 20)
    rng = np.random.default_rng(42)
    features = pd.DataFrame(
        rng.normal(size=(len(labels), len(FEATURE_COLUMNS))),
        columns=FEATURE_COLUMNS,
    )
    features["V1"] = labels * 8 + rng.normal(scale=0.2, size=len(labels))
    model = make_pipeline(
        StandardScaler(),
        LogisticRegression(random_state=42, max_iter=1000),
    )
    model.fit(features, labels)
    return model


@pytest.fixture
def test_client(tmp_path, monkeypatch):
    artifacts_dir = tmp_path / "artifacts"
    artifacts_dir.mkdir()
    joblib.dump(fit_test_model(), artifacts_dir / "model.joblib")
    (artifacts_dir / "threshold.json").write_text(
        json.dumps({"threshold": 0.5, "min_precision": 0.8}),
        encoding="utf-8",
    )
    (artifacts_dir / "metrics.json").write_text(
        json.dumps(
            {
                "model_version": "test-v1",
                "trained_at": "2026-10-26T00:00:00+00:00",
                "precision": 0.91,
                "recall": 0.82,
                "f1": 0.86,
                "roc_auc": 0.97,
                "pr_auc": 0.95,
                "confusion_matrix": [[100, 2], [3, 10]],
                "date": "this must not appear in model info",
                "split_sizes": {"train": 100},
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(model_loader, "MODEL_PATH", artifacts_dir / "model.joblib")
    monkeypatch.setattr(
        model_loader, "THRESHOLD_PATH", artifacts_dir / "threshold.json"
    )
    monkeypatch.setattr(
        model_loader, "METRICS_PATH", artifacts_dir / "metrics.json"
    )
    monkeypatch.delenv("ML_API_KEY", raising=False)
    with TestClient(app) as client:
        yield client


def test_health_reports_loaded_model(test_client) -> None:
    response = test_client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "model_loaded",
        "model_loaded": True,
        "model_version": "test-v1",
    }

def test_cors_allows_only_configured_client_url(test_client) -> None:
    configured_origin = os.getenv("CLIENT_URL", "http://localhost:5173")
    rejected_origin = (
        "https://untrusted.example"
        if configured_origin != "https://untrusted.example"
        else "https://another-untrusted.example"
    )

    allowed = test_client.options(
        "/health",
        headers={
            "Origin": configured_origin,
            "Access-Control-Request-Method": "GET",
        },
    )
    rejected = test_client.options(
        "/health",
        headers={
            "Origin": rejected_origin,
            "Access-Control-Request-Method": "GET",
        },
    )

    assert allowed.headers["access-control-allow-origin"] == configured_origin
    assert "access-control-allow-origin" not in rejected.headers


def test_prediction_rejects_missing_feature(test_client) -> None:
    invalid = transaction()
    invalid.pop("V28")

    response = test_client.post("/predict", json=invalid)

    assert response.status_code == 422


def test_prediction_rejects_negative_amount(test_client) -> None:
    response = test_client.post("/predict", json=transaction(amount=-0.01))

    assert response.status_code == 422


def test_batch_prediction_returns_three_results(test_client) -> None:
    response = test_client.post(
        "/predict/batch",
        json=[transaction(v1=-1), transaction(v1=0), transaction(v1=1)],
    )

    assert response.status_code == 200
    assert len(response.json()) == 3


def test_batch_prediction_rejects_more_than_100_rows(test_client) -> None:
    response = test_client.post(
        "/predict/batch",
        json=[transaction() for _ in range(101)],
    )

    assert response.status_code == 422


def test_model_info_includes_metrics_and_saved_threshold(test_client) -> None:
    response = test_client.get("/model-info")

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {
        "model_version",
        "threshold",
        "min_precision",
        "trained_at",
        "metrics",
    }
    assert body == {
        "model_version": "test-v1",
        "threshold": 0.5,
        "min_precision": 0.8,
        "trained_at": "2026-10-26T00:00:00+00:00",
        "metrics": {
            "precision": 0.91,
            "recall": 0.82,
            "f1": 0.86,
            "roc_auc": 0.97,
            "pr_auc": 0.95,
            "confusion_matrix": [[100, 2], [3, 10]],
        },
    }


def test_wrong_api_key_is_rejected_when_key_is_configured(
    test_client, monkeypatch
) -> None:
    monkeypatch.setenv("ML_API_KEY", "expected-secret")

    response = test_client.post(
        "/predict",
        json=transaction(),
        headers={"X-API-Key": "wrong-secret"},
    )

    assert response.status_code == 401


def test_startup_reports_missing_model_artifact(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(model_loader, "MODEL_PATH", tmp_path / "missing-model.joblib")

    with pytest.raises(FileNotFoundError, match="Required model artifact is missing"):
        model_loader.load_model_artifacts()


def test_startup_reports_missing_trained_at_metadata(tmp_path, monkeypatch) -> None:
    artifacts_dir = tmp_path / "artifacts"
    artifacts_dir.mkdir()
    joblib.dump(fit_test_model(), artifacts_dir / "model.joblib")
    (artifacts_dir / "threshold.json").write_text(
        json.dumps({"threshold": 0.5, "min_precision": 0.8}),
        encoding="utf-8",
    )
    (artifacts_dir / "metrics.json").write_text(
        json.dumps({"model_version": "test-v1"}),
        encoding="utf-8",
    )
    monkeypatch.setattr(model_loader, "MODEL_PATH", artifacts_dir / "model.joblib")
    monkeypatch.setattr(
        model_loader, "THRESHOLD_PATH", artifacts_dir / "threshold.json"
    )
    monkeypatch.setattr(
        model_loader, "METRICS_PATH", artifacts_dir / "metrics.json"
    )

    with pytest.raises(RuntimeError, match="trained_at"):
        model_loader.load_model_artifacts()


def test_replay_fraud_average_probability_exceeds_genuine_average() -> None:
    service_dir = Path(__file__).resolve().parents[1]
    replay_path = service_dir / "data" / "replay_samples.json"
    required_artifacts = [
        model_loader.MODEL_PATH,
        model_loader.THRESHOLD_PATH,
        model_loader.METRICS_PATH,
        replay_path,
    ]
    missing = [path for path in required_artifacts if not path.is_file()]
    if missing:
        pytest.skip(
            "Requires finalized model artifacts and data/replay_samples.json: "
            + ", ".join(str(path) for path in missing)
        )

    replay_rows = json.loads(replay_path.read_text(encoding="utf-8"))
    fraud_rows = [row for row in replay_rows if row["Class"] == 1]
    genuine_rows = [row for row in replay_rows if row["Class"] == 0]
    if not fraud_rows or not genuine_rows:
        pytest.skip("Replay data must contain both fraud and genuine rows.")

    fraud_probabilities = []
    genuine_probabilities = []
    with TestClient(app) as client:
        # The batch API caps each request at 100, so replay every row in chunks.
        for start in range(0, len(replay_rows), 100):
            chunk = replay_rows[start : start + 100]
            response = client.post(
                "/predict/batch",
                json=[
                    {column: row[column] for column in FEATURE_COLUMNS}
                    for row in chunk
                ],
            )
            assert response.status_code == 200
            for row, prediction in zip(chunk, response.json()):
                target = (
                    fraud_probabilities if row["Class"] == 1 else genuine_probabilities
                )
                target.append(prediction["fraud_probability"])

    # Probabilities vary with the fitted model and data, so check only the intended ranking.
    assert np.mean(fraud_probabilities) > np.mean(genuine_probabilities)
