"""Compare four fraud classifiers using training data and validation data only."""

from pathlib import Path
from time import perf_counter

import matplotlib.pyplot as plt
import pandas as pd
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.preprocessing import RobustScaler
from xgboost import XGBClassifier


SERVICE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = SERVICE_DIR / "data" / "processed"
ARTIFACTS_DIR = SERVICE_DIR / "artifacts"
LABEL_COLUMN = "Class"
SCALED_COLUMNS = ["Time", "Amount"]
FEATURE_COLUMNS = ["Time", *[f"V{i}" for i in range(1, 29)], "Amount"]
RANDOM_STATE = 42
THRESHOLD = 0.5


def load_splits(
    train_path: Path = DATA_DIR / "train.csv",
    validation_path: Path = DATA_DIR / "val.csv",
) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series]:
    """Load and validate only the training and validation splits."""
    train = pd.read_csv(train_path)
    validation = pd.read_csv(validation_path)

    for name, split in (("training", train), ("validation", validation)):
        missing = [column for column in [*FEATURE_COLUMNS, LABEL_COLUMN] if column not in split]
        if missing:
            raise ValueError(f"{name} data is missing required columns: {', '.join(missing)}")
        if split.empty:
            raise ValueError(f"{name} data contains no rows.")
        if split[[*FEATURE_COLUMNS, LABEL_COLUMN]].isna().any().any():
            raise ValueError(f"{name} data contains missing feature values or labels.")
        if not set(split[LABEL_COLUMN].unique()).issubset({0, 1}):
            raise ValueError(f"{name} labels must be binary values 0 and 1.")

    if train[LABEL_COLUMN].nunique() != 2:
        raise ValueError("Training data must contain both genuine and fraud examples.")
    if validation[LABEL_COLUMN].nunique() != 2:
        raise ValueError("Validation data must contain both genuine and fraud examples.")

    return (
        train[FEATURE_COLUMNS],
        train[LABEL_COLUMN].astype(int),
        validation[FEATURE_COLUMNS],
        validation[LABEL_COLUMN].astype(int),
    )


def make_preprocessor() -> ColumnTransformer:
    """Scale transaction time and amount while passing PCA features unchanged."""
    return ColumnTransformer(
        transformers=[("scale", RobustScaler(), SCALED_COLUMNS)],
        remainder="passthrough",
        verbose_feature_names_out=False,
    )


def build_models(y_train: pd.Series) -> dict[str, Pipeline]:
    """Create model pipelines with preprocessing fitted only during training."""
    genuine_count = int((y_train == 0).sum())
    fraud_count = int((y_train == 1).sum())
    if fraud_count == 0 or genuine_count == 0:
        raise ValueError("Training data must contain both genuine and fraud examples.")
    if fraud_count < 2:
        raise ValueError("SMOTE requires at least two fraud examples in training data.")

    def make_smote() -> SMOTE:
        return SMOTE(
            random_state=RANDOM_STATE,
            k_neighbors=min(5, fraud_count - 1),
        )

    models = {
        "A. Balanced Logistic Regression": [
            ("preprocessing", make_preprocessor()),
            (
                "classifier",
                LogisticRegression(
                    class_weight="balanced",
                    random_state=RANDOM_STATE,
                    max_iter=1000,
                ),
            ),
        ],
        "B. SMOTE + Logistic Regression": [
            ("preprocessing", make_preprocessor()),
            ("smote", make_smote()),
            (
                "classifier",
                LogisticRegression(random_state=RANDOM_STATE, max_iter=1000),
            ),
        ],
        "C. XGBoost": [
            ("preprocessing", make_preprocessor()),
            (
                "classifier",
                XGBClassifier(
                    random_state=RANDOM_STATE,
                    scale_pos_weight=genuine_count / fraud_count,
                    eval_metric="logloss",
                    n_jobs=1,
                ),
            ),
        ],
        "D. SMOTE + XGBoost": [
            ("preprocessing", make_preprocessor()),
            ("smote", make_smote()),
            (
                "classifier",
                XGBClassifier(
                    random_state=RANDOM_STATE,
                    eval_metric="logloss",
                    n_jobs=1,
                ),
            ),
        ],
    }
    return {name: Pipeline(steps) for name, steps in models.items()}


def compare_models(
    x_train: pd.DataFrame,
    y_train: pd.Series,
    x_validation: pd.DataFrame,
    y_validation: pd.Series,
    artifacts_dir: Path = ARTIFACTS_DIR,
) -> pd.DataFrame:
    """Fit each pipeline on training data and evaluate it on validation data."""
    models = build_models(y_train)
    metrics = []
    curves = []

    for name, model in models.items():
        start = perf_counter()
        model.fit(x_train, y_train)
        training_time = perf_counter() - start

        probabilities = model.predict_proba(x_validation)[:, 1]
        predictions = (probabilities >= THRESHOLD).astype(int)
        precision_curve, recall_curve, _ = precision_recall_curve(
            y_validation, probabilities
        )
        metrics.append(
            {
                "model": name,
                "precision": precision_score(
                    y_validation, predictions, zero_division=0
                ),
                "recall": recall_score(y_validation, predictions, zero_division=0),
                "f1": f1_score(y_validation, predictions, zero_division=0),
                "roc_auc": roc_auc_score(y_validation, probabilities),
                "pr_auc": average_precision_score(y_validation, probabilities),
                "training_time_seconds": training_time,
            }
        )
        curves.append((name, precision_curve, recall_curve))

    results = pd.DataFrame(metrics)
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    results.to_csv(artifacts_dir / "model_comparison.csv", index=False)

    figure, axis = plt.subplots(figsize=(9, 7))
    for name, precision_curve, recall_curve in curves:
        axis.plot(recall_curve, precision_curve, label=name)
    axis.set_title("Validation precision-recall curves")
    axis.set_xlabel("Recall")
    axis.set_ylabel("Precision")
    axis.legend()
    axis.grid(alpha=0.25)
    figure.tight_layout()
    figure.savefig(artifacts_dir / "pr_curves.png", dpi=150)
    plt.close(figure)

    return results


def main() -> None:
    x_train, y_train, x_validation, y_validation = load_splits()
    results = compare_models(x_train, y_train, x_validation, y_validation)
    print(results.to_string(index=False))

    best = results.loc[results["pr_auc"].idxmax()]
    print(
        f"\nBest validation PR-AUC: {best['model']} "
        f"({best['pr_auc']:.4f})."
    )
    print(
        "PR-AUC focuses on precision and recall for the fraud class, so it shows "
        "how well models rank rare fraud cases without the many genuine "
        "transactions dominating the score. ROC-AUC can look strong on highly "
        "imbalanced data because its false-positive rate is measured against "
        "the very large genuine class."
    )


if __name__ == "__main__":
    main()
