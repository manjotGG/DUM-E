"""Final evaluation uses one final observed row per official test engine."""
import json
import time
from pathlib import Path

import joblib
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error

from .preprocess import data_directory, load_labels, load_trajectories, make_features


def regression_metrics(actual, predicted):
    return {"mae": float(mean_absolute_error(actual, predicted)), "rmse": float(np.sqrt(mean_squared_error(actual, predicted)))}


def evaluate_artifact(artifact, directory=None):
    directory = Path(directory) if directory else data_directory()
    frame = load_trajectories(directory / "test_FD001.txt")
    labels = load_labels(directory / "RUL_FD001.txt", frame.engine_id.unique())
    last = frame.groupby("engine_id", sort=True).tail(1)
    features = make_features(frame).loc[last.index, artifact["feature_names"]]
    start = time.perf_counter()
    predicted = np.maximum(0, artifact["pipeline"].predict(features))
    batch_ms = (time.perf_counter() - start) * 1000
    actual = labels.loc[last.engine_id].to_numpy()
    points = [{"engine_id": int(engine), "cycle": int(cycle), "actual_rul": float(a), "predicted_rul": float(p), "error": float(p-a)}
              for engine, cycle, a, p in zip(last.engine_id, last.cycle, actual, predicted)]
    errors = predicted - actual
    counts, edges = np.histogram(errors, bins=12)
    ranges = []
    for lower, upper in [(0, 30), (30, 60), (60, 100), (100, float("inf"))]:
        mask = (actual >= lower) & (actual < upper)
        if mask.any():
            ranges.append({"range": f"{lower}–{int(upper) if np.isfinite(upper) else '∞'}", "count": int(mask.sum()), **regression_metrics(actual[mask], predicted[mask])})
    # End-to-end timing includes feature generation on one complete observed prefix.
    prefix = frame[frame.engine_id == 1]
    timings = []
    for _ in range(10):
        start = time.perf_counter()
        artifact["pipeline"].predict(make_features(prefix).iloc[[-1]][artifact["feature_names"]])
        timings.append((time.perf_counter() - start) * 1000)
    return {
        **regression_metrics(actual, predicted), "evaluation_status": "complete", "evaluation_engines": len(actual),
        "evaluation_protocol": "Official uncapped RUL labels at the last observed cycle of each FD001 test engine. Test data unused for model selection.",
        "predictions": points, "error_by_rul": ranges,
        "error_distribution": [{"lower": float(edges[i]), "upper": float(edges[i+1]), "count": int(count)} for i, count in enumerate(counts)],
        "inference_latency_ms": float(np.median(timings)), "batch_inference_ms": batch_ms,
    }


def main():
    from .train import model_directory
    directory = model_directory()
    artifact = joblib.load(directory / "model.joblib")
    report = json.loads((directory / "metrics.json").read_text())
    report.update(evaluate_artifact(artifact))
    (directory / "metrics.json").write_text(json.dumps(report, indent=2))
    print(json.dumps({key: report[key] for key in ["mae", "rmse", "inference_latency_ms"]}, indent=2))

if __name__ == "__main__":
    main()
