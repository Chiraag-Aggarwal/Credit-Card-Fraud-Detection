import pandas as pd

from training.prepare_data import prepare_data


def test_prepare_data_saves_raw_stratified_splits(tmp_path) -> None:
    dataset = pd.DataFrame(
        {
            "Time": range(100),
            "Amount": [float(value) / 10 for value in range(100)],
            "Class": [0] * 90 + [1] * 10,
        }
    )
    input_path = tmp_path / "creditcard.csv"
    output_dir = tmp_path / "processed"
    dataset.to_csv(input_path, index=False)

    splits = prepare_data(input_path, output_dir)

    assert {name: len(split) for name, split in splits.items()} == {
        "train": 60,
        "val": 20,
        "test": 20,
    }
    assert {name: int(split["Class"].sum()) for name, split in splits.items()} == {
        "train": 6,
        "val": 2,
        "test": 2,
    }
    for name, split in splits.items():
        saved = pd.read_csv(output_dir / f"{name}.csv")
        pd.testing.assert_frame_equal(
            saved, split.reset_index(drop=True), check_dtype=False
        )
        assert set(saved.columns) == set(dataset.columns)
