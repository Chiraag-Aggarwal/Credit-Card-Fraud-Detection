import json
from pathlib import Path
from typing import Any

import joblib


ARTIFACTS_DIR = Path(__file__).resolve().parents[1] / "artifacts"
MODEL_PATH = ARTIFACTS_DIR / "model.joblib"
THRESHOLD_PATH = ARTIFACTS_DIR / "threshold.json"
METRICS_PATH = ARTIFACTS_DIR / "metrics.json"


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"Required model artifact is missing: {path}")
    try:
        content = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError(f"Could not read model artifact {path}: {error}") from error
    if not isinstance(content, dict):
        raise RuntimeError(f"Model artifact must contain a JSON object: {path}")
    return content


def load_model_artifacts() -> tuple[Any, float, dict[str, Any], str]:
    """Load the model and its metadata once as the API starts."""
    if not MODEL_PATH.is_file():
        raise FileNotFoundError(f"Required model artifact is missing: {MODEL_PATH}")
    try:
        model = joblib.load(MODEL_PATH)
    except Exception as error:
        raise RuntimeError(f"Could not load model artifact {MODEL_PATH}: {error}") from error

    threshold_data = _read_json(THRESHOLD_PATH)
    metrics = _read_json(METRICS_PATH)
    threshold = threshold_data.get("threshold")
    if isinstance(threshold, bool) or not isinstance(threshold, (int, float)):
        raise RuntimeError(f"Artifact {THRESHOLD_PATH} must contain a numeric threshold.")
    if not 0 <= threshold <= 1:
        raise RuntimeError(f"Artifact threshold must be between 0 and 1: {THRESHOLD_PATH}")

    model_version = metrics.get("model_version")
    if not isinstance(model_version, str) or not model_version.strip():
        raise RuntimeError(
            f"Artifact {METRICS_PATH} must contain a non-empty model_version."
        )
    return model, float(threshold), metrics, model_version
