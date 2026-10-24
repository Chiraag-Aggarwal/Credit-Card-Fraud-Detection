import json

import joblib
import numpy as np
import pandas as pd
import pytest

from training.finalize_model import choose_threshold, finalize_model


def test_choose_threshold_uses_lowest_value_meeting_precision_floor() -> None:
    threshold, precision, _, thresholds, selected_index = choose_threshold(
        pd.Series([0, 0, 1, 1]),
        np.array([0.1, 0.4, 0.6, 0.9]),
        min_precision=0.8,
    )

    assert threshold == thresholds[selected_index]
    assert precision[selected_index] >= 0.8
    assert selected_index == 2


def test_finalize_model_saves_pipeline_threshold_metrics_and_heatmap(tmp_path) -> None:
    rng = np.random.default_rng(42)
    labels = np.tile([0, 0, 0, 0, 1], 24)
    features = pd.DataFrame(
        {
            "Time": rng.normal(size=120),
            "Amount": rng.normal(size=120),
            **{f"V{i}": rng.normal(size=120) for i in range(1, 29)},
        }
    )
    features["V1"] = labels + rng.normal(scale=0.1, size=120)

    metrics = finalize_model(
        features.iloc[:60],
        pd.Series(labels[:60]),
        features.iloc[60:90],
        pd.Series(labels[60:90]),
        features.iloc[90:],
        pd.Series(labels[90:]),
        artifacts_dir=tmp_path,
        model_name="A",
        min_precision=0.8,
    )

    assert metrics["split_sizes"] == {"train": 60, "validation": 30, "test": 30}
    matrix = np.array(metrics["confusion_matrix"])
    assert matrix.sum() == 30
    assert matrix[1].sum() == 6
    assert matrix[1, 0] == 0
    assert metrics["model_version"] == "logistic-regression-v1"
    assert joblib.load(tmp_path / "model.joblib").predict(features.iloc[:2]).shape == (2,)
    assert json.loads((tmp_path / "threshold.json").read_text())["min_precision"] == 0.8
    assert json.loads((tmp_path / "metrics.json").read_text())["pr_auc"] == metrics["pr_auc"]
    assert (tmp_path / "confusion_matrix.png").is_file()


def test_choose_threshold_fails_if_precision_floor_is_unattainable() -> None:
    with pytest.raises(ValueError, match="No validation threshold"):
        choose_threshold(
            pd.Series([0, 0, 1, 1]),
            np.array([0.1, 0.8, 0.2, 0.3]),
            min_precision=1.0,
        )
