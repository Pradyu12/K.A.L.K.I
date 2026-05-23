import pytest
from fastapi.testclient import TestClient
from main import app
import os

# Mock DB initialization for testing
@pytest.fixture(autouse=True)
def mock_db(monkeypatch):
    async def mock_init():
        pass
    async def mock_log(*args, **kwargs):
        pass
    monkeypatch.setattr("main.init_db", mock_init)
    monkeypatch.setattr("main.log_command", mock_log)

client = TestClient(app)

def test_health_check():
    # health check is not in main.py anymore, but let's check index
    response = client.get("/")
    assert response.status_code == 200
    assert "KALKI HUD" in response.text

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
    # This test will trigger the 'offline' response if no API key is present
    # which still contains 'sir'
    response = client.post(
        "/api/v1/command",
        json={"command": "Who are you?", "timestamp": "2023-10-27T12:00:00Z"}
    )
    assert response.status_code == 200
    assert "sir" in response.json()["response"].lower()
