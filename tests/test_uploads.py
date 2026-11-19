import json

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.services.log_parser import MAX_BYTES, parse_log
from ml.engines.metadata import SENSOR_METADATA
from ml.engines.preprocess import data_directory, load_trajectories


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="module")
def engine():
    frame = load_trajectories(data_directory() / "test_FD001.txt")
    return frame[frame.engine_id == 1].copy()


def encode(frame, symbols=False, header=True, sep=","):
    if symbols:
        frame = frame.rename(columns={s["key"]: s["symbol"] for s in SENSOR_METADATA})
    return frame.to_csv(index=False, header=header, sep=sep).encode()


def test_sensor_schema_and_downloadable_real_sample(client, engine):
    schema = client.get("/api/engines/log-schema").json()
    assert schema["minimum_cycles"] == 15 and len(schema["columns"]) == 26
    assert len(schema["sensors"]) == 21
    assert schema["sensors"][1] == {"key": "sensor_2", "symbol": "T24", "name": "LPC outlet temperature", "unit": "°R"}
    response = client.get("/api/engines/sample-log")
    assert response.status_code == 200 and "text/csv" in response.headers["content-type"]
    assert "attachment" in response.headers["content-disposition"]
    pd.testing.assert_frame_equal(parse_log(response.content), engine, check_dtype=False)


@pytest.mark.parametrize("symbols,header,sep", [(False, True, ","), (True, True, ","), (False, False, " "), (True, True, "\t"), (False, False, ",")])
def test_upload_matches_model_prediction(client, engine, symbols, header, sep):
    response = client.post("/api/engines/analyze-log", content=encode(engine, symbols, header, sep))
    assert response.status_code == 200, response.text
    data = response.json()
    expected = client.post("/api/engines/predict", json={"engine_id": 1, "cycle": 31}).json()
    assert data["rows"] == 31 and data["engines_analyzed"] == 1
    prediction = data["predictions"][0]
    assert prediction["predicted_rul"] == expected["predicted_rul"]
    assert prediction["explanation"] == expected["explanation"]
    assert prediction["source"] == "upload" and prediction["observations"] == 31
    assert len(data["histories"][0]["history"]) == 31


def test_multiple_engines_and_later_prefix_have_identical_features(client, engine):
    # Engine identifiers are grouping keys, not model inputs. The last 15 cycles
    # contain the complete longest feature window, so the prediction is identical.
    first = engine.tail(15).copy(); first["engine_id"] = 42
    second = engine.copy(); second["engine_id"] = 900
    response = client.post("/api/engines/analyze-log", content=encode(pd.concat([first, second])))
    assert response.status_code == 200
    data = response.json()
    assert data["engines_analyzed"] == 2
    assert [p["engine_id"] for p in data["predictions"]] == [42, 900]
    assert data["predictions"][0]["predicted_rul"] == data["predictions"][1]["predicted_rul"]
    assert data["predictions"][0]["first_cycle"] == 17


@pytest.mark.parametrize("kind,message", [("short", "15 consecutive"), ("gap", "consecutive"), ("duplicate", "duplicates"), ("reversed", "increasing"), ("nan", "missing"), ("infinity", "non-finite"), ("overflow", "numeric range"), ("columns", "26"), ("fractional", "whole numbers"), ("header_only", "no observations"), ("text", "numeric"), ("negative_id", "positive"), ("ambiguous_header", "Header")])
def test_upload_validation(client, engine, kind, message):
    frame = engine.copy()
    if kind == "short": frame = frame.head(14)
    if kind == "gap": frame = frame.drop(frame.index[10])
    if kind == "duplicate": frame.loc[frame.index[5], "cycle"] = 5
    if kind == "reversed": frame = frame.iloc[::-1]
    if kind == "nan": frame.loc[frame.index[0], "sensor_2"] = float("nan")
    if kind == "infinity": frame.loc[frame.index[0], "sensor_2"] = float("inf")
    if kind == "overflow": frame.loc[frame.index[0], "sensor_2"] = 1e300
    if kind == "columns": frame = frame.drop(columns=["sensor_21"])
    if kind == "fractional": frame["engine_id"] = 2.5
    if kind == "negative_id": frame["engine_id"] = -1
    if kind == "header_only": frame = frame.head(0)
    if kind == "text": frame = frame.astype(object); frame.loc[frame.index[0], "sensor_2"] = "hello"
    if kind == "ambiguous_header": frame = frame.rename(columns={"sensor_2": "T2"})
    response = client.post("/api/engines/analyze-log", content=encode(frame, header=kind != "columns"))
    assert response.status_code == 422, response.text
    assert message in response.json()["detail"], response.text


@pytest.mark.parametrize("content", [b"", b"\x00\x00", b"\xff\xfe"])
def test_empty_or_binary_log(client, content):
    assert client.post("/api/engines/analyze-log", content=content).status_code == 422


def test_upload_limit(client):
    response = client.post("/api/engines/analyze-log", content=b"0" * (MAX_BYTES + 1))
    assert response.status_code == 413


def test_upload_model_unavailable_and_dataset_independence(client, monkeypatch, engine):
    with monkeypatch.context() as patch:
        patch.setattr(app.state.engines, "artifact", None)
        assert client.post("/api/engines/analyze-log", content=encode(engine)).status_code == 503
    with monkeypatch.context() as patch:
        patch.setattr(app.state.engines, "frame", None)
        response = client.post("/api/engines/analyze-log", content=encode(engine))
        assert response.status_code == 200
        assert client.get("/api/engines/sample-log").status_code == 503
