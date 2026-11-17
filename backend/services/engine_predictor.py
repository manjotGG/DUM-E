import json
import logging
import os
import time

import numpy as np
from fastapi import HTTPException

from backend.predictor import artifact_directory, load_engine_artifact
from ml.engines.preprocess import COLUMNS, SENSORS, data_directory, load_trajectories, make_features

logger = logging.getLogger(__name__)
LIMITATION = "Estimate from NASA simulated degradation data. Priority thresholds are configurable demonstration rules, not validated aircraft maintenance limits."


class EngineService:
    def __init__(self):
        self.frame = None
        self.artifact = None
        self.metrics = None
        self.critical = float(os.getenv("CRITICAL_RUL", "30"))
        self.elevated = float(os.getenv("ELEVATED_RUL", "60"))
        if not (np.isfinite([self.critical, self.elevated]).all() and 0 < self.critical < self.elevated):
            raise ValueError("Priority thresholds must satisfy 0 < CRITICAL_RUL < ELEVATED_RUL.")
        try:
            self.frame = load_trajectories(data_directory() / "test_FD001.txt")
        except Exception:
            logger.exception("Could not load the FD001 test dataset")
        try:
            self.artifact = load_engine_artifact()
            # Warm model and verify feature compatibility during startup.
            if self.frame is not None:
                features = make_features(self.frame[self.frame.engine_id == 1]).iloc[[-1]]
                self.artifact["pipeline"].predict(features[self.artifact["feature_names"]])
        except Exception:
            self.artifact = None
            logger.exception("Could not load the engine model")
        try:
            self.metrics = json.loads((artifact_directory() / "metrics.json").read_text())
        except (OSError, ValueError):
            logger.warning("Evaluation report unavailable")

    def require_data(self):
        if self.frame is None:
            raise HTTPException(503, "FD001 data unavailable. Configure CMAPSS_DATA_DIR and restart the backend.")

    def engines(self):
        self.require_data()
        return {"dataset": "FD001", "split": "test", "sensors": SENSORS,
                "engines": [{"engine_id": int(engine), "available_cycles": int(group.cycle.max()), "observations": len(group)}
                            for engine, group in self.frame.groupby("engine_id")]}

    def prefix(self, engine_id, cycle=None):
        self.require_data()
        frame = self.frame[self.frame.engine_id == engine_id]
        if frame.empty:
            raise HTTPException(404, "Engine not found in FD001 test trajectories.")
        maximum = int(frame.cycle.max())
        if cycle is not None and (cycle < 1 or cycle > maximum):
            raise HTTPException(422, f"Cycle unavailable. Engine {engine_id} has observed cycles 1–{maximum}.")
        return frame if cycle is None else frame[frame.cycle <= cycle]

    def history(self, engine_id, cycle=None):
        prefix = self.prefix(engine_id, cycle)
        return {"engine_id": engine_id, "dataset": "FD001", "split": "test", "latest_cycle": int(prefix.cycle.max()),
                "observations": len(prefix), "sensors": SENSORS, "history": prefix[COLUMNS].to_dict(orient="records")}

    def predict(self, engine_id, cycle=None):
        prefix = self.prefix(engine_id, cycle)
        if self.artifact is None:
            raise HTTPException(503, "Engine model unavailable. Run python -m ml.engines.train and restart the backend.")
        start = time.perf_counter()
        features = make_features(prefix).iloc[[-1]][self.artifact["feature_names"]]
        value = float(self.artifact["pipeline"].predict(features)[0])
        if not np.isfinite(value):
            raise HTTPException(503, "Model returned an invalid estimate. Retrain the engine model.")
        value = max(0, value)
        priority = "Critical" if value < self.critical else "Elevated" if value < self.elevated else "Normal"
        return {"engine_id": engine_id, "current_cycle": int(prefix.cycle.max()), "predicted_rul": round(value, 2),
                "maintenance_priority": priority, "model_version": self.artifact["model_version"], "model_name": self.artifact["model_name"],
                "rul_unit": "cycles", "inference_ms": round((time.perf_counter() - start) * 1000, 2),
                "thresholds": {"critical_below": self.critical, "elevated_below": self.elevated}, "limitation": LIMITATION}
