"""Local model contributions, using the fitted pipeline and observed prefix only."""
import numpy as np
from xgboost import DMatrix

from ml.engines.metadata import SENSOR_METADATA
from ml.engines.preprocess import WINDOW


def explain_prediction(artifact, features, prefix):
    pipeline = artifact["pipeline"]
    estimator = pipeline.named_steps["estimator"]
    if not hasattr(estimator, "get_booster"):
        return {"available": False, "summary": "Sensor contributions are unavailable for this model."}

    # Native TreeSHAP operates on the same filtered/scaled inputs as inference.
    transformed = pipeline[:-1].transform(features)
    names = np.asarray(artifact["feature_names"])[pipeline.named_steps["variance"].get_support()]
    contributions = estimator.get_booster().predict(DMatrix(transformed), pred_contribs=True)[0]
    if len(contributions) != len(names) + 1 or not np.isfinite(contributions).all():
        raise ValueError("Invalid model contribution output.")
    by_feature = dict(zip(names, map(float, contributions[:-1])))
    sensors = []
    for sensor in SENSOR_METADATA:
        key = sensor["key"]
        # Group current reading, trailing means, variability and trend together.
        matching = {name: value for name, value in by_feature.items()
                    if name == key or name.startswith(key + "_")}
        if not matching:
            continue
        recent = prefix.tail(WINDOW)
        sensors.append({**sensor, "contribution_cycles": sum(matching.values()),
                        "reading": float(prefix[key].iloc[-1]),
                        "recent_change": float(recent[key].iloc[-1] - recent[key].iloc[0]),
                        "observed_window": len(recent)})
    sensors.sort(key=lambda sensor: sensor["contribution_cycles"])
    other = {name: value for name, value in by_feature.items() if not name.startswith("sensor_")}
    return {"available": True, "method": "TreeSHAP", "baseline_cycles": float(contributions[-1]),
            "sensor_contributions": sensors, "other_contributions": other,
            "raw_prediction_cycles": float(np.sum(contributions, dtype=np.float64)),
            "summary": "Contributions compare this estimate with the model’s training-data baseline. "
                       "Each sensor includes its reading and history features; negative values lower the estimate. "
                       "These explain model behaviour, not a confirmed physical fault."}
