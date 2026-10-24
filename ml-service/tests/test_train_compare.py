import numpy as np
import pandas as pd

from training.train_compare import compare_models, make_preprocessor


def test_preprocessor_scales_only_time_and_amount() -> None:
    features = pd.DataFrame(
        {
            "Time": [0.0, 10.0, 20.0],
            "V1": [1.0, 2.0, 3.0],
            "Amount": [100.0, 200.0, 300.0],
        }
    )
    transformed = make_preprocessor().fit_transform(features)

    np.testing.assert_allclose(transformed[:, 2], features["V1"])
    assert transformed.shape == features.shape


def test_compare_models_saves_validation_metrics_and_pr_plot(tmp_path) -> None:
    rng = np.random.default_rng(42)
    labels = np.tile([0, 0, 0, 0, 1], 12)
    features = pd.DataFrame(
        {
            "Time": rng.normal(size=60),
            "Amount": rng.normal(size=60),
            **{f"V{i}": rng.normal(size=60) for i in range(1, 29)},
        }
    )
    features["V1"] = labels + rng.normal(scale=0.1, size=60)
    x_train = features.iloc[:40]
    y_train = pd.Series(labels[:40])
    x_validation = features.iloc[40:]
    y_validation = pd.Series(labels[40:])

    results = compare_models(
        x_train,
        y_train,
        x_validation,
        y_validation,
        artifacts_dir=tmp_path,
    )

    assert len(results) == 4
    assert {
        "precision",
        "recall",
        "f1",
        "roc_auc",
        "pr_auc",
        "training_time_seconds",
    }.issubset(results.columns)
    assert results["training_time_seconds"].gt(0).all()
    assert (tmp_path / "model_comparison.csv").is_file()
    assert (tmp_path / "pr_curves.png").is_file()
