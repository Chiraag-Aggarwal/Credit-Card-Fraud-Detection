import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from training.explain import explain_model
from training.train_compare import FEATURE_COLUMNS


def test_explain_model_saves_top_fifteen_validation_features(tmp_path) -> None:
    rng = np.random.default_rng(42)
    labels = np.tile([0, 0, 0, 0, 1], 20)
    features = pd.DataFrame(
        rng.normal(size=(len(labels), len(FEATURE_COLUMNS))),
        columns=FEATURE_COLUMNS,
    )
    features["V1"] = labels + rng.normal(scale=0.1, size=len(labels))
    model = make_pipeline(
        StandardScaler(),
        LogisticRegression(random_state=42, max_iter=1000),
    )
    model.fit(features.iloc[:60], labels[:60])

    model_path = tmp_path / "model.joblib"
    validation_path = tmp_path / "val.csv"
    output_path = tmp_path / "artifacts" / "feature_importance.png"
    joblib.dump(model, model_path)
    validation = features.iloc[60:].copy()
    validation["Class"] = labels[60:]
    validation.to_csv(validation_path, index=False)

    importance = explain_model(model_path, validation_path, output_path)

    assert len(importance) == 15
    assert importance["importance_mean"].is_monotonic_increasing
    assert output_path.is_file()
