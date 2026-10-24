"""Focused tests for the fraud-model pipeline."""

import pandas as pd

from train_model import FEATURE_COLUMNS, create_model_pipeline


def test_pipeline_trains_and_returns_fraud_probabilities() -> None:
    rows = []
    labels = []
    for index in range(40):
        rows.append(
            {
                column: float(index % 4 == 0) if column == "V1" else float(index)
                for column in FEATURE_COLUMNS
            }
        )
        labels.append(int(index % 4 == 0))

    features = pd.DataFrame(rows, columns=FEATURE_COLUMNS)
    model = create_model_pipeline()
    model.fit(features, labels)

    probabilities = model.predict_proba(features)
    assert probabilities.shape == (40, 2)
    assert ((probabilities >= 0) & (probabilities <= 1)).all()
