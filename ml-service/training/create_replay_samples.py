"""Create a small demo replay file from the held-out test split."""

import json
from pathlib import Path

import pandas as pd


SERVICE_DIR = Path(__file__).resolve().parents[1]
TEST_PATH = SERVICE_DIR / "data" / "processed" / "test.csv"
OUTPUT_PATH = SERVICE_DIR / "data" / "replay_samples.json"
FEATURE_COLUMNS = ["Time", *[f"V{i}" for i in range(1, 29)], "Amount"]
LABEL_COLUMN = "Class"
SAMPLE_SIZE = 300
MAX_FRAUD_ROWS = 60
RANDOM_STATE = 42


def create_replay_samples(
    test_path: Path = TEST_PATH,
    output_path: Path = OUTPUT_PATH,
) -> pd.DataFrame:
    """Sample test transactions without replacement and save raw values as JSON."""
    test_data = pd.read_csv(test_path)
    required_columns = [*FEATURE_COLUMNS, LABEL_COLUMN]
    missing = [column for column in required_columns if column not in test_data]
    if missing:
        raise ValueError(f"Test split is missing required columns: {', '.join(missing)}")
    if test_data.empty:
        raise ValueError(f"Test split contains no rows: {test_path}")
    if test_data[required_columns].isna().any().any():
        raise ValueError("Test split contains missing feature values or labels.")
    if not set(test_data[LABEL_COLUMN].unique()).issubset({0, 1}):
        raise ValueError("Test labels must be binary values 0 and 1.")

    # Keep only the raw input features and true label; model scores are not replay inputs.
    test_data = test_data[required_columns]
    fraud = test_data.loc[test_data[LABEL_COLUMN] == 1]
    genuine = test_data.loc[test_data[LABEL_COLUMN] == 0]

    # Cap fraud examples at 60 so the demo stays imbalanced without hiding fraud entirely.
    fraud_count = min(MAX_FRAUD_ROWS, len(fraud))
    genuine_count = SAMPLE_SIZE - fraud_count
    if len(genuine) < genuine_count:
        raise ValueError(
            f"Need {SAMPLE_SIZE} test rows with at most {MAX_FRAUD_ROWS} fraud rows; "
            f"found {len(genuine)} genuine and {len(fraud)} fraud."
        )

    # Sample each class without replacement so every replay row is an actual test row.
    samples = pd.concat(
        [
            genuine.sample(n=genuine_count, random_state=RANDOM_STATE),
            fraud.sample(n=fraud_count, random_state=RANDOM_STATE),
        ]
    )
    # Shuffle after stratified selection so records are not grouped by their true label.
    samples = samples.sample(frac=1, random_state=RANDOM_STATE).reset_index(drop=True)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(samples.to_dict(orient="records"), indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(
        f"Saved {len(samples)} replay rows "
        f"({int(samples[LABEL_COLUMN].sum())} fraud) to {output_path}"
    )
    return samples


if __name__ == "__main__":
    create_replay_samples()
