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
