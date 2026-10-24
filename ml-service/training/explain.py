"""Explain a saved fraud model with validation-set permutation importance."""

from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.inspection import permutation_importance

from training.train_compare import (
    ARTIFACTS_DIR,
    DATA_DIR,
    FEATURE_COLUMNS,
    LABEL_COLUMN,
)


MODEL_PATH = ARTIFACTS_DIR / "model.joblib"
VALIDATION_PATH = DATA_DIR / "val.csv"
OUTPUT_PATH = ARTIFACTS_DIR / "feature_importance.png"
TOP_FEATURE_COUNT = 15
RANDOM_STATE = 42
N_REPEATS = 5


def explain_model(
    model_path: Path = MODEL_PATH,
    validation_path: Path = VALIDATION_PATH,
    output_path: Path = OUTPUT_PATH,
) -> pd.DataFrame:
    """Calculate validation PR-AUC permutation importance and save its chart."""
    if not model_path.is_file():
        raise FileNotFoundError(f"Saved model not found: {model_path}")
    if not validation_path.is_file():
        raise FileNotFoundError(f"Validation split not found: {validation_path}")

    validation = pd.read_csv(validation_path)
    required_columns = [*FEATURE_COLUMNS, LABEL_COLUMN]
    missing = [column for column in required_columns if column not in validation]
    if missing:
        raise ValueError(
            f"Validation data is missing required columns: {', '.join(missing)}"
        )
    if validation.empty:
        raise ValueError(f"Validation split contains no rows: {validation_path}")
    if validation[required_columns].isna().any().any():
        raise ValueError("Validation data contains missing features or labels.")
    if not set(validation[LABEL_COLUMN].unique()).issubset({0, 1}):
        raise ValueError("Validation labels must be binary values 0 and 1.")
    if validation[LABEL_COLUMN].nunique() != 2:
        raise ValueError("Validation data must contain both classes.")

    model = joblib.load(model_path)
    result = permutation_importance(
        model,
        validation[FEATURE_COLUMNS],
        validation[LABEL_COLUMN].astype(int),
        scoring="average_precision",
        n_repeats=N_REPEATS,
        random_state=RANDOM_STATE,
        n_jobs=1,
    )
    importance = (
        pd.DataFrame(
            {
                "feature": FEATURE_COLUMNS,
                "importance_mean": result.importances_mean,
                "importance_std": result.importances_std,
            }
        )
        .sort_values("importance_mean", ascending=False)
        .head(TOP_FEATURE_COUNT)
        .sort_values("importance_mean", ascending=True)
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure, axis = plt.subplots(figsize=(9, 7))
    axis.barh(
        importance["feature"],
        importance["importance_mean"],
        xerr=importance["importance_std"],
        color="#4C78A8",
        alpha=0.85,
        capsize=3,
    )
    axis.axvline(0, color="black", linewidth=0.8)
    axis.set_title("Top 15 feature permutation importance (validation PR-AUC)")
    axis.set_xlabel("Decrease in average precision when feature is shuffled")
    axis.set_ylabel("Feature")
    axis.grid(axis="x", alpha=0.25)
    # Longer bars mean shuffling that feature reduced validation PR-AUC more.
    # Bars near zero suggest the model relied little on that feature in this sample.
    # Negative bars can occur when shuffling helps, so treat them as weak or noisy signals.
    figure.tight_layout()
    figure.savefig(output_path, dpi=150)
    plt.close(figure)
    return importance.reset_index(drop=True)


def main() -> None:
    importance = explain_model()
    print(importance.to_string(index=False))
    print(f"\nSaved feature importance chart to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
