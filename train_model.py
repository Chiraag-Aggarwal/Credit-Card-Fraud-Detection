"""Train and evaluate a credit-card fraud classifier."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


DATA_PATH = Path("data/creditcard.csv")
MODEL_PATH = Path("models/fraud_detection_model.joblib")
METRICS_PATH = Path("models/metrics.json")
LABEL_COLUMN = "Class"
FEATURE_COLUMNS = ["Time", *[f"V{i}" for i in range(1, 29)], "Amount"]
RANDOM_STATE = 42


def create_model_pipeline() -> Pipeline:
    """Build the preprocessing and classification pipeline."""
    preprocessing = ColumnTransformer(
        transformers=[("scale", StandardScaler(), ["Time", "Amount"])],
        remainder="passthrough",
    )
    return Pipeline(
        steps=[
            ("preprocessing", preprocessing),
            (
                "classifier",
                LogisticRegression(
                    class_weight="balanced",
                    max_iter=1000,
                    random_state=RANDOM_STATE,
                ),
            ),
        ]
    )


def load_dataset(path: Path = DATA_PATH) -> tuple[pd.DataFrame, pd.Series]:
    """Load the Kaggle CSV and validate its required columns and labels."""
    if not path.is_file():
        raise FileNotFoundError(
            f"Dataset not found at {path}. Download creditcard.csv from Kaggle "
            "and place it in the data directory."
        )

    dataset = pd.read_csv(path)
    missing = [column for column in [*FEATURE_COLUMNS, LABEL_COLUMN] if column not in dataset]
    if missing:
        raise ValueError(f"Dataset is missing required columns: {', '.join(missing)}")
    if dataset.empty:
        raise ValueError("Dataset contains no transaction rows.")

    features = dataset[FEATURE_COLUMNS]
    labels = dataset[LABEL_COLUMN]
    if features.isna().any().any() or labels.isna().any():
        raise ValueError("Dataset contains missing feature values or labels.")
    if not set(labels.unique()).issubset({0, 1}):
        raise ValueError("Class labels must be binary values 0 and 1.")
    if labels.nunique() != 2:
        raise ValueError("Dataset must contain examples of both classes.")

    return features, labels.astype(int)


def train_and_evaluate(
    features: pd.DataFrame, labels: pd.Series
) -> tuple[Pipeline, dict[str, object]]:
    """Fit a stratified model and return held-out classification metrics."""
    x_train, x_test, y_train, y_test = train_test_split(
        features,
        labels,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=labels,
    )
    model = create_model_pipeline()
    model.fit(x_train, y_train)

    probabilities = model.predict_proba(x_test)[:, 1]
    predictions = (probabilities >= 0.5).astype(int)
    metrics: dict[str, object] = {
        "threshold": 0.5,
        "test_rows": int(len(y_test)),
        "precision": float(precision_score(y_test, predictions, zero_division=0)),
        "recall": float(recall_score(y_test, predictions, zero_division=0)),
        "f1": float(f1_score(y_test, predictions, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_test, probabilities)),
        "average_precision": float(average_precision_score(y_test, probabilities)),
        "confusion_matrix": confusion_matrix(y_test, predictions).tolist(),
    }
    return model, metrics


def main() -> None:
    features, labels = load_dataset()
    model, metrics = train_and_evaluate(features, labels)

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    METRICS_PATH.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")

    print(f"Saved model to {MODEL_PATH}")
    print(f"Saved evaluation metrics to {METRICS_PATH}")
    for name, value in metrics.items():
        print(f"{name}: {value}")


if __name__ == "__main__":
    main()
