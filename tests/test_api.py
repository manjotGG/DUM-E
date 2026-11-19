import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as client:
        yield client


def test_health_and_inventory(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["milling_model_loaded"] is False
    engines = client.get("/api/engines").json()["engines"]
    assert len(engines) == 100
    assert engines[0] == {"engine_id": 1, "available_cycles": 31, "observations": 31}


def test_history_prefix_never_exposes_future(client):
    data = client.get("/api/engines/1/history?cycle=10").json()
    assert data["latest_cycle"] == data["observations"] == len(data["history"]) == 10
    assert max(row["cycle"] for row in data["history"]) == 10
    assert len(data["history"][0]) == 26
    assert client.get("/api/engines/1/history").json()["latest_cycle"] == 31


def test_prediction_matches_saved_final_test_output(client):
    response = client.post("/api/engines/predict", json={"engine_id": 1, "cycle": 31})
    assert response.status_code == 200
    data = response.json()
    report = client.get("/api/engines/metrics").json()
    assert data["predicted_rul"] == pytest.approx(report["predictions"][0]["predicted_rul"], abs=.01)
    assert data["predicted_rul"] >= 0 and data["rul_unit"] == "cycles"
    assert data["maintenance_priority"] in {"Critical", "Elevated", "Normal"}
    assert data["model_version"] == report["model_version"]
    assert data["inference_ms"] < 500
    assert client.post("/api/engines/predict", json={"engine_id": 1}).json()["current_cycle"] == 31
    assert client.post("/api/engines/predict", json={"engine_id": 1, "cycle": 1}).status_code == 200


@pytest.mark.parametrize("payload, status", [({}, 422), ({"engine_id": 999}, 404), ({"engine_id": 0}, 422),
    ({"engine_id": 1, "cycle": 32}, 422), ({"engine_id": 1, "cycle": 0}, 422),
    ({"engine_id": "1"}, 422), ({"engine_id": True}, 422), ({"engine_id": 1, "cycle": 2.5}, 422),
    ({"engine_id": 1, "unexpected": 5}, 422)])
def test_invalid_prediction_input(client, payload, status):
    assert client.post("/api/engines/predict", json=payload).status_code == status


def test_invalid_history_and_inactive_milling(client):
    assert client.get("/api/engines/999/history").status_code == 404
    assert client.get("/api/engines/1/history?cycle=32").status_code == 422
    assert client.get("/api/engines/1/history?cycle=-1").status_code == 422
    assert client.post("/api/milling/predict", json={}).status_code == 501


def test_model_and_dataset_unavailable(client, monkeypatch):
    with monkeypatch.context() as patch:
        patch.setattr(app.state.engines, "artifact", None)
        assert client.get("/health").json()["status"] == "degraded"
        response = client.post("/api/engines/predict", json={"engine_id": 1})
        assert response.status_code == 503 and "model unavailable" in response.json()["detail"]
    with monkeypatch.context() as patch:
        patch.setattr(app.state.engines, "frame", None)
        assert client.get("/api/engines").status_code == 503
    with monkeypatch.context() as patch:
        patch.setattr(app.state.engines, "metrics", None)
        assert client.get("/api/engines/metrics").status_code == 503


def test_cors_allows_only_configured_origins(client):
    allowed = client.options("/api/engines/predict", headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "POST"})
    assert allowed.headers["access-control-allow-origin"] == "http://localhost:5173"
    denied = client.options("/api/engines/predict", headers={"Origin": "https://untrusted.example", "Access-Control-Request-Method": "POST"})
    assert "access-control-allow-origin" not in denied.headers


def test_configurable_thresholds(client, monkeypatch):
    service = app.state.engines
    with monkeypatch.context() as patch:
        patch.setattr(service, "critical", 10000)
        patch.setattr(service, "elevated", 20000)
        data = client.post("/api/engines/predict", json={"engine_id": 1}).json()
        assert data["maintenance_priority"] == "Critical"
        assert data["thresholds"] == {"critical_below": 10000, "elevated_below": 20000}


def test_built_dashboard_served_by_backend(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "DUM-E" in response.text and 'id="root"' in response.text


@pytest.mark.parametrize("engine_id,cycle", [(1, 1), (1, 31), (100, 198)])
def test_sensor_explanation_reconciles_with_prediction(client, engine_id, cycle):
    data = client.post("/api/engines/predict", json={"engine_id": engine_id, "cycle": cycle}).json()
    explanation = data["explanation"]
    assert explanation["available"] and explanation["method"] == "TreeSHAP"
    sensors = explanation["sensor_contributions"]
    assert len(sensors) == 14
    assert [s["contribution_cycles"] for s in sensors] == sorted(s["contribution_cycles"] for s in sensors)
    total = explanation["baseline_cycles"] + sum(s["contribution_cycles"] for s in sensors) + sum(explanation["other_contributions"].values())
    assert total == pytest.approx(explanation["raw_prediction_cycles"], abs=1e-5)
    assert max(0, total) == pytest.approx(data["predicted_rul"], abs=.01)
    history = client.get(f"/api/engines/{engine_id}/history?cycle={cycle}").json()["history"]
    for sensor in sensors:
        assert sensor["reading"] == history[-1][sensor["key"]]
        assert sensor["observed_window"] == min(cycle, 15)
        assert sensor["recent_change"] == pytest.approx(history[-1][sensor["key"]] - history[-min(cycle, 15)][sensor["key"]])
    if engine_id == 100:
        assert data["maintenance_priority"] == "Critical"
        assert sensors[0]["contribution_cycles"] < 0


def test_explanation_uses_no_future_observations(client, monkeypatch):
    service = app.state.engines
    before = service.predict(1, 10)
    changed = service.frame.copy()
    changed.loc[(changed.engine_id == 1) & (changed.cycle > 10), "sensor_11"] = 99999
    with monkeypatch.context() as patch:
        patch.setattr(service, "frame", changed)
        after = service.predict(1, 10)
    assert before["explanation"] == after["explanation"]
    assert before["predicted_rul"] == after["predicted_rul"]


def test_explanation_failure_preserves_prediction(client, monkeypatch):
    def fail(*args):
        raise ValueError("Explanation failed")
    monkeypatch.setattr("backend.services.engine_predictor.explain_prediction", fail)
    response = client.post("/api/engines/predict", json={"engine_id": 1})
    assert response.status_code == 200
    assert response.json()["predicted_rul"] > 0
    assert response.json()["explanation"]["available"] is False
