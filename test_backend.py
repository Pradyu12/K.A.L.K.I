import pytest
from fastapi.testclient import TestClient
from main import app
import os

@pytest.fixture(autouse=True)
def mock_db(monkeypatch):
    async def mock_init():
        pass
    async def mock_log(*args, **kwargs):
        pass
    async def mock_get_logs(limit=10):
        return [('test', 'response', '2023-10-27T12:00:00Z')]
    async def mock_clear():
        pass
    monkeypatch.setattr("main.init_db", mock_init)
    monkeypatch.setattr("main.log_command", mock_log)
    monkeypatch.setattr("main.get_recent_logs", mock_get_logs)
    monkeypatch.setattr("main.clear_logs", mock_clear)

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_index():
    response = client.get("/")
    assert response.status_code == 200
    assert "J.A.R.V.I.S. HUD" in response.text

def test_diagnostics_intent():
    response = client.post(
        "/api/v1/command",
        json={"command": "system diagnostics", "timestamp": "2023-10-27T12:00:00Z"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "diagnostics"
    assert "sir" in data["response"].lower()

def test_ai_fallback_persona():
    response = client.post(
        "/api/v1/command",
        json={"command": "Who are you?", "timestamp": "2023-10-27T12:00:00Z"}
    )
    assert response.status_code == 200
    assert "sir" in response.json()["response"].lower()

def test_get_logs():
    response = client.get("/api/v1/logs")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "logs" in data

def test_clear_logs():
    response = client.delete("/api/v1/logs")
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_stats():
    response = client.get("/api/v1/stats")
    assert response.status_code == 200
    assert response.json()["status"] == "success"