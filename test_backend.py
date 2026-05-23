import pytest
from fastapi.testclient import TestClient
from main import app
import database
import os

# Mock DB operations to avoid side effects during testing
@pytest.fixture(autouse=True)
def mock_db(monkeypatch):
    async def mock_init():
        pass
    async def mock_log(*args, **kwargs):
        pass
    async def mock_add_task(*args, **kwargs):
        pass
    async def mock_get_tasks(*args, **kwargs):
        return [(1, "Test Mission", "Desc", "pending", "high", "2023-10-27")]

    monkeypatch.setattr("database.init_db", mock_init)
    monkeypatch.setattr("database.log_command", mock_log)
    monkeypatch.setattr("database.add_task", mock_add_task)
    monkeypatch.setattr("database.get_tasks", mock_get_tasks)

client = TestClient(app)

def test_hud_access():
    response = client.get("/")
    assert response.status_code == 200
    assert "MISSION_LOG" in response.text

def test_task_add_intent():
    response = client.post(
        "/api/v1/command",
        json={"command": "add task finish the project", "timestamp": "2023-10-27T12:00:00Z"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "task_add"
    assert "mission" in data["response"].lower()
    assert "sir" in data["response"].lower()

def test_task_list_intent():
    response = client.post(
        "/api/v1/command",
        json={"command": "list my missions", "timestamp": "2023-10-27T12:00:00Z"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "task_list"
    assert "Test Mission" in data["response"]

def test_file_intent():
    response = client.post(
        "/api/v1/command",
        json={"command": "list files in current directory", "timestamp": "2023-10-27T12:00:00Z"}
    )
    assert response.status_code == 200
    assert "Scanning directory" in response.json()["response"]

def test_tasks_api():
    response = client.get("/api/v1/tasks")
    assert response.status_code == 200
    assert "tasks" in response.json()
    assert len(response.json()["tasks"]) > 0
