"""Load only trusted, locally generated artifacts; never accept uploaded pickle files."""
import os
from pathlib import Path

import joblib

from ml.engines.preprocess import ROOT


def artifact_directory():
    return Path(os.getenv("ENGINE_MODEL_DIR", ROOT / "ml/models/engines"))


def load_engine_artifact(directory=None):
    artifact = joblib.load((Path(directory) if directory else artifact_directory()) / "model.joblib")
    for key in ["pipeline", "feature_names", "model_name", "model_version", "config"]:
        if key not in artifact:
            raise ValueError("Model artifact is incomplete. Retrain using python -m ml.engines.train.")
    return artifact
