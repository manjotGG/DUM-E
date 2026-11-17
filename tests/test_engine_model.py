import json

import joblib
import numpy as np
import pandas as pd
import pytest

from backend.predictor import artifact_directory, load_engine_artifact
from ml.engines.preprocess import COLUMNS, data_directory, generate_targets, inspect, load_labels, load_trajectories, make_features


@pytest.fixture(scope="module")
def train():
    return load_trajectories(data_directory() / "train_FD001.txt")


def test_supplied_data_and_label_alignment():
    report = inspect()
    assert report["train_engines"] == report["test_engines"] == report["official_labels"] == 100
    assert report["columns"] == 26 and report["missing_values"] == 0
    assert report["train_rows"] == 20631 and report["test_rows"] == 13096
    test = load_trajectories(data_directory() / "test_FD001.txt")
    labels = load_labels(data_directory() / "RUL_FD001.txt", test.engine_id.unique())
    assert labels.index.tolist() == list(range(1, 101))
    assert labels.loc[1] == 112 and test[test.engine_id == 1].cycle.max() == 31


def test_targets_are_run_to_failure(train):
    targets = generate_targets(train)
    last = train.groupby("engine_id").tail(1)
    assert (targets.loc[last.index] == 0).all()
    assert targets.iloc[0] == 191
    assert generate_targets(train, 125).max() == 125


def test_features_are_causal_and_engine_local(train):
    full = make_features(train)
    assert "engine_id" not in full
    first = train[(train.engine_id == 1) & (train.cycle <= 40)]
    pd.testing.assert_frame_equal(full.loc[first.index], make_features(first))
    second = train[(train.engine_id == 2) & (train.cycle <= 22)]
    pd.testing.assert_frame_equal(full.loc[second.index], make_features(second))
    mutated = train.copy()
    mutated.loc[(mutated.engine_id == 1) & (mutated.cycle > 40), "sensor_2"] = 99999
    pd.testing.assert_frame_equal(full.loc[first.index], make_features(mutated).loc[first.index])
    assert np.isfinite(full.to_numpy()).all()


@pytest.mark.parametrize("mutation", ["column", "nan", "duplicate", "order", "fractional_id"])
def test_bad_trajectories_rejected(tmp_path, train, mutation):
    frame = train[train.engine_id == 1].head(5).copy()
    if mutation == "column": frame = frame.drop(columns=["sensor_21"])
    if mutation == "nan": frame.loc[0, "sensor_2"] = np.inf
    if mutation == "duplicate": frame.loc[1, "cycle"] = 1
    if mutation == "order": frame = frame.iloc[::-1]
    if mutation == "fractional_id": frame["engine_id"] = 1.5
    path = tmp_path / "bad.txt"
    frame.to_csv(path, sep=" ", index=False, header=False)
    with pytest.raises(ValueError): load_trajectories(path)


def test_bad_labels_rejected(tmp_path):
    path = tmp_path / "RUL.txt"
    path.write_text("1\n2\n")
    with pytest.raises(ValueError): load_labels(path, [1])
    path.write_text("-2\n")
    with pytest.raises(ValueError): load_labels(path, [1])


def test_saved_model_and_evaluation(tmp_path):
    artifact = load_engine_artifact()
    report = json.loads((artifact_directory() / "metrics.json").read_text())
    config = report["training_config"]
    assert not set(config["train_engines"]) & set(config["validation_engines"])
    assert len(config["train_engines"]) + len(config["validation_engines"]) == 100
    chosen = min(report["model_comparison"], key=lambda row: row["rmse"])
    assert artifact["model_name"] == chosen["name"]
    assert report["evaluation_engines"] == len(report["predictions"]) == 100
    assert sum(row["count"] for row in report["error_distribution"]) == 100
    assert np.isfinite([report["mae"], report["rmse"], report["inference_latency_ms"]]).all()
    assert report["rmse"] >= report["mae"] > 0
    test = load_trajectories(data_directory() / "test_FD001.txt")
    features = make_features(test[test.engine_id == 1]).iloc[[-1]]
    assert features.columns.tolist() == artifact["feature_names"]
    before = artifact["pipeline"].predict(features)
    joblib.dump(artifact, tmp_path / "model.joblib")
    after = joblib.load(tmp_path / "model.joblib")["pipeline"].predict(features)
    np.testing.assert_allclose(before, after)
    assert max(0, before[0]) == pytest.approx(report["predictions"][0]["predicted_rul"])
