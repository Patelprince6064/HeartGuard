"""Model registry for HeartGuard.

Provides functions for saving, loading, and managing trained models.
Keeps a registry of available models and tracks the best performer.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib

from config.settings import MODEL_DIRECTORY
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Canonical model names
MODEL_NAMES: list[str] = [
    "logistic_regression",
    "random_forest",
    "xgboost",
    "neural_network",
]

MODEL_FILENAMES: dict[str, str] = {
    "logistic_regression": "logistic_regression.pkl",
    "random_forest": "random_forest.pkl",
    "xgboost": "xgboost.pkl",
    "neural_network": "neural_network.pkl",
}


def get_model_path(model_name: str) -> Path:
    """Get the file path for a saved model.

    Args:
        model_name: Canonical model name.

    Returns:
        Path to the model file.
    """
    filename = MODEL_FILENAMES.get(model_name, f"{model_name}.pkl")
    return MODEL_DIRECTORY / filename


def save_model(model: Any, model_name: str) -> Path:
    """Save a trained model to disk.

    Args:
        model: Trained model object.
        model_name: Canonical model name.

    Returns:
        Path to saved model file.
    """
    path = get_model_path(model_name)
    path.parent.mkdir(parents=True, exist_ok=True)

    joblib.dump(model, path)

    logger.info("Model '%s' saved to %s", model_name, path)
    return path


def load_model(model_name: str) -> Any:
    """Load a trained model from disk.

    Args:
        model_name: Canonical model name.

    Returns:
        Loaded model object.

    Raises:
        FileNotFoundError: If model file does not exist.
    """
    path = get_model_path(model_name)
    if not path.exists():
        raise FileNotFoundError(f"Model file not found: {path}")

    model = joblib.load(path)
    logger.info("Model '%s' loaded from %s", model_name, path)
    return model


def get_available_models() -> list[str]:
    """List models that have saved files on disk.

    Returns:
        List of model names with existing files.
    """
    available = []
    for name in MODEL_NAMES:
        path = get_model_path(name)
        if path.exists():
            available.append(name)
    return available


def get_best_model_name() -> str | None:
    """Get the name of the best model from the saved results.

    Returns:
        Model name string, or None if no results exist.
    """
    results_path = MODEL_DIRECTORY.parent / "reports" / "model_results.json"
    if not results_path.exists():
        return None
    with open(results_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    best = data.get("best_model", {})
    return best.get("model_name")


def register_model(
    model_name: str,
    metadata: dict[str, Any],
    output_dir: str | Path | None = None,
) -> Path:
    """Register model metadata to the model metadata file.

    Args:
        model_name: Canonical model name.
        metadata: Model metadata dictionary.
        output_dir: Directory for the metadata file.

    Returns:
        Path to the metadata file.
    """
    if output_dir is None:
        output_dir = MODEL_DIRECTORY
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)
    metadata_path = output_dir / "model_metadata.json"

    if metadata_path.exists():
        with open(metadata_path, "r", encoding="utf-8") as f:
            all_metadata = json.load(f)
    else:
        all_metadata = {}

    all_metadata[model_name] = metadata

    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(all_metadata, f, indent=2, default=str)

    logger.info("Model '%s' registered in %s", model_name, metadata_path)
    return metadata_path
