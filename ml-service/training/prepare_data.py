"""Create raw, stratified dataset splits before preprocessing.

Splitting first keeps information from validation and test data out of training.
If scaling or resampling is done before the split, the training data can learn
from the held-out data and make evaluation results look better than they are.
"""

from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split


SERVICE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = SERVICE_DIR / "data" / "creditcard.csv"
OUTPUT_DIR = SERVICE_DIR / "data" / "processed"
LABEL_COLUMN = "Class"
RANDOM_STATE = 42


def prepare_data(
    input_path: Path = DATA_PATH,
    output_dir: Path = OUTPUT_DIR,
) -> dict[str, pd.DataFrame]:
    """Save raw stratified train, validation, and test CSV files."""
    data = pd.read_csv(input_path)
    if data.empty:
        raise ValueError(f"Dataset is empty: {input_path}")
    if LABEL_COLUMN not in data.columns:
        raise ValueError(f"Dataset must contain a '{LABEL_COLUMN}' column.")
    if data[LABEL_COLUMN].isna().any():
        raise ValueError(f"Dataset contains missing values in '{LABEL_COLUMN}'.")

    train, remaining = train_test_split(
        data,
        test_size=0.4,
        random_state=RANDOM_STATE,
        stratify=data[LABEL_COLUMN],
    )
    validation, test = train_test_split(
        remaining,
        test_size=0.5,
        random_state=RANDOM_STATE,
        stratify=remaining[LABEL_COLUMN],
    )

    splits = {"train": train, "val": validation, "test": test}
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, split in splits.items():
        split.to_csv(output_dir / f"{name}.csv", index=False)
        fraud_count = int((split[LABEL_COLUMN] == 1).sum())
        print(f"{name}: {len(split):,} rows, {fraud_count:,} fraud")

    return splits


if __name__ == "__main__":
    prepare_data()
