"""python -m ml.engines.train: group validation, selection, refit, final test."""
import copy
import hashlib
import json
import os
import platform
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import sklearn
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_selection import VarianceThreshold
from sklearn.linear_model import Ridge
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor

from .evaluate import evaluate_artifact, regression_metrics
from .preprocess import ROOT, WINDOW, data_directory, generate_targets, inspect, load_trajectories, make_features

SEED = 42
VERSION = "1.0.0"


def model_directory():
    return Path(os.getenv("ENGINE_MODEL_DIR", ROOT / "ml/models/engines"))


def validation_indices(frame, indices):
    """Three censored prefixes per held-out engine, approximating partially observed test histories."""
    held = frame.loc[indices]
    return [group.index[max(0, int(len(group) * fraction) - 1)]
            for _, group in held.groupby("engine_id") for fraction in [.35, .55, .75]]


def candidates():
    forest = RandomForestRegressor(n_estimators=180, max_depth=14, min_samples_leaf=4, max_features=.8, n_jobs=4, random_state=SEED)
    boost = XGBRegressor(n_estimators=550, max_depth=4, learning_rate=.035, subsample=.85, colsample_bytree=.85, reg_lambda=8, objective="reg:squarederror", n_jobs=4, random_state=SEED)
    return [("Constant baseline", DummyRegressor(), None), ("Ridge regression", Ridge(alpha=100), None),
            ("Random Forest", forest, None), ("Random Forest · capped 125", copy.deepcopy(forest), 125),
            ("XGBoost", boost, None), ("XGBoost · capped 125", copy.deepcopy(boost), 125)]


def main():
    directory = data_directory()
    output = model_directory()
    output.mkdir(parents=True, exist_ok=True)
    frame = load_trajectories(directory / "train_FD001.txt")
    features = make_features(frame)
    targets = generate_targets(frame)
    train_idx, held_idx = next(GroupShuffleSplit(n_splits=1, test_size=.2, random_state=SEED).split(features, targets, groups=frame.engine_id))
    valid_idx = validation_indices(frame, held_idx)
    train_engines = sorted(int(x) for x in frame.loc[train_idx].engine_id.unique())
    valid_engines = sorted(int(x) for x in frame.loc[held_idx].engine_id.unique())
    config = {"seed": SEED, "window": WINDOW, "subset": "FD001", "train_engines": train_engines,
              "validation_engines": valid_engines, "validation_prefix_fractions": [.35, .55, .75],
              "validation_points": len(valid_idx), "selection_metric": "uncapped validation RMSE",
              "output_policy": "Predictions clipped at zero, expressed only in cycles.",
              "python": platform.python_version(), "scikit_learn": sklearn.__version__,
              "dataset_sha256": {f: hashlib.sha256((directory / f).read_bytes()).hexdigest() for f in ["train_FD001.txt", "test_FD001.txt", "RUL_FD001.txt"]}}
    results, pipelines = [], {}
    for name, estimator, cap in candidates():
        print(f"Training {name}...", flush=True)
        pipeline = Pipeline([("variance", VarianceThreshold()), ("scale", StandardScaler()), ("estimator", estimator)])
        pipeline.fit(features.iloc[train_idx], targets.iloc[train_idx].clip(upper=cap) if cap else targets.iloc[train_idx])
        prediction = np.maximum(0, pipeline.predict(features.loc[valid_idx]))
        result = {"name": name, "rul_cap": cap, **regression_metrics(targets.loc[valid_idx], prediction)}
        results.append(result)
        pipelines[name] = pipeline
        print(json.dumps(result), flush=True)
    best = min(results, key=lambda row: row["rmse"])
    selected = pipelines[best["name"]]
    print(f"Refitting {best['name']} on all 100 training engines...", flush=True)
    selected.fit(features, targets.clip(upper=best["rul_cap"]) if best["rul_cap"] else targets)
    config["rul_cap"] = best["rul_cap"]
    artifact = {"pipeline": selected, "feature_names": features.columns.tolist(), "model_name": best["name"], "model_version": VERSION, "config": config}
    joblib.dump(artifact, output / "model.joblib", compress=3)
    # Verify serialization before producing final test results.
    artifact = joblib.load(output / "model.joblib")
    transformed_names = np.array(features.columns)[selected.named_steps["variance"].get_support()]
    estimator = selected.named_steps["estimator"]
    weights = getattr(estimator, "feature_importances_", None)
    importance_kind = "tree impurity / gain importance"
    if weights is None and hasattr(estimator, "coef_"):
        weights = np.abs(estimator.coef_)
        importance_kind = "absolute standardized ridge coefficient"
    importance = sorted([{"feature": str(f), "importance": float(w)} for f, w in zip(transformed_names, weights)], key=lambda x: x["importance"], reverse=True)[:20] if weights is not None else []
    report = {"model_name": best["name"], "model_version": VERSION, "trained_at": datetime.now(timezone.utc).isoformat(),
              "training_config": config, "model_comparison": results, "feature_importance": importance,
              "importance_kind": importance_kind, "dataset": inspect(directory), **evaluate_artifact(artifact, directory)}
    (output / "metrics.json").write_text(json.dumps(report, indent=2))
    print(json.dumps({key: report[key] for key in ["model_name", "mae", "rmse", "inference_latency_ms"]}, indent=2), flush=True)

if __name__ == "__main__":
    main()
