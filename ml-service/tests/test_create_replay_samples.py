import json

import pandas as pd
import pytest

from training.create_replay_samples import (
    FEATURE_COLUMNS,
    create_replay_samples,
)


def test_create_replay_samples_uses_raw_test_rows_and_caps_fraud(tmp_path) -> None:
    dataset = pd.DataFrame(
        {
            column: [float(index) for index in range(400)]
            for column in FEATURE_COLUMNS
        }
    )
    dataset["Class"] = [0] * 300 + [1] * 100
    source = tmp_path / "test.csv"
    output = tmp_path / "data" / "replay_samples.json"
    dataset.to_csv(source, index=False)

    samples = create_replay_samples(source, output)

    saved_records = json.loads(output.read_text(encoding="utf-8"))
    assert len(samples) == 300
    assert len(saved_records) == 300
    assert int(samples["Class"].sum()) == 60
    assert list(samples.columns) == [*FEATURE_COLUMNS, "Class"]
    assert set(map(tuple, samples.to_numpy())) <= set(map(tuple, dataset.to_numpy()))


def test_create_replay_samples_rejects_test_split_with_too_few_rows(tmp_path) -> None:
    dataset = pd.DataFrame(
        {
            column: [float(index) for index in range(20)]
            for column in FEATURE_COLUMNS
        }
    )
    dataset["Class"] = [0] * 18 + [1] * 2
    source = tmp_path / "small_test.csv"
    dataset.to_csv(source, index=False)

    with pytest.raises(ValueError, match="Need 300 test rows"):
        create_replay_samples(source, tmp_path / "replay_samples.json")
