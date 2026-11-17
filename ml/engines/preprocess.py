"""Strict ingestion and causal features shared by training and inference."""
import os
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SENSORS = [f"sensor_{i}" for i in range(1, 22)]
SETTINGS = [f"setting_{i}" for i in range(1, 4)]
COLUMNS = ["engine_id", "cycle", *SETTINGS, *SENSORS]
# FD001 channels carrying degradation information; constant channels are excluded.
ACTIVE_SENSORS = [f"sensor_{i}" for i in [2, 3, 4, 7, 8, 9, 11, 12, 13, 14, 15, 17, 20, 21]]
WINDOW = 15


def data_directory():
    if os.getenv("CMAPSS_DATA_DIR"):
        return Path(os.environ["CMAPSS_DATA_DIR"]).expanduser()
    for candidate in [ROOT / "data/engines/raw", ROOT / "CMAPSSData", ROOT.parent / "CMAPSSData"]:
        if (candidate / "train_FD001.txt").exists():
            return candidate
    raise FileNotFoundError("FD001 data unavailable. Set CMAPSS_DATA_DIR to the dataset directory.")


def load_trajectories(path):
    frame = pd.read_csv(path, sep=r"\s+", header=None)
    if frame.shape[1] != len(COLUMNS) or frame.empty:
        raise ValueError("C-MAPSS trajectories require 26 numeric columns and at least one row.")
    frame.columns = COLUMNS
    frame = frame.apply(pd.to_numeric, errors="raise")
    if not np.isfinite(frame.to_numpy()).all():
        raise ValueError("Dataset contains missing or non-finite values.")
    for col in ["engine_id", "cycle"]:
        if (frame[col] < 1).any() or (frame[col] % 1 != 0).any():
            raise ValueError("Engine IDs and cycles must be positive integers.")
        frame[col] = frame[col].astype(int)
    ids = sorted(frame.engine_id.unique())
    if ids != list(range(1, len(ids) + 1)):
        raise ValueError("Dataset engine IDs must be contiguous starting at one.")
    for _, group in frame.groupby("engine_id", sort=True):
        if group.cycle.tolist() != list(range(1, len(group) + 1)):
            raise ValueError("Each trajectory must contain ordered, unique, consecutive cycles starting at one.")
    return frame.sort_values(["engine_id", "cycle"]).reset_index(drop=True)


def load_labels(path, engine_ids):
    raw = pd.read_csv(path, sep=r"\s+", header=None)
    if raw.shape != (len(engine_ids), 1):
        raise ValueError("Official RUL labels must align one-to-one with sorted test engine IDs.")
    labels = raw.iloc[:, 0].to_numpy(dtype=float)
    if not np.isfinite(labels).all() or (labels < 0).any() or (labels % 1 != 0).any():
        raise ValueError("Official RUL labels must be finite nonnegative integers.")
    return pd.Series(labels, index=sorted(engine_ids), name="actual_rul")


def generate_targets(frame, cap=None):
    target = frame.groupby("engine_id").cycle.transform("max") - frame.cycle
    return target.clip(upper=cap) if cap is not None else target


def make_features(frame):
    """Every row depends only on that engine's prefix, never future observations."""
    frame = frame.sort_values(["engine_id", "cycle"])
    features = frame[["cycle", *SETTINGS, *ACTIVE_SENSORS]].astype(float).copy()
    grouped = frame.groupby("engine_id", sort=False)
    for sensor in ACTIVE_SENSORS:
        series = grouped[sensor]
        features[f"{sensor}_mean_{WINDOW}"] = series.transform(lambda s: s.rolling(WINDOW, min_periods=1).mean())
        features[f"{sensor}_std_{WINDOW}"] = series.transform(lambda s: s.rolling(WINDOW, min_periods=1).std(ddof=0))
        features[f"{sensor}_trend_{WINDOW}"] = series.diff(WINDOW - 1).fillna(0) / (WINDOW - 1)
        features[f"{sensor}_mean_5"] = series.transform(lambda s: s.rolling(5, min_periods=1).mean())
    return features


def inspect(directory=None):
    directory = Path(directory) if directory else data_directory()
    train = load_trajectories(directory / "train_FD001.txt")
    test = load_trajectories(directory / "test_FD001.txt")
    labels = load_labels(directory / "RUL_FD001.txt", test.engine_id.unique())
    return {
        "subset": "FD001", "train_rows": len(train), "test_rows": len(test),
        "train_engines": int(train.engine_id.nunique()), "test_engines": int(test.engine_id.nunique()),
        "official_labels": len(labels), "columns": len(COLUMNS), "missing_values": int(train.isna().sum().sum() + test.isna().sum().sum()),
        "constant_columns": [c for c in [*SETTINGS, *SENSORS] if train[c].nunique() == 1],
        "sensor_statistics": {s: {"min": float(train[s].min()), "max": float(train[s].max()), "std": float(train[s].std())} for s in SENSORS},
        "source": "NASA C-MAPSS supplied files; simulated turbofan degradation trajectories",
    }
