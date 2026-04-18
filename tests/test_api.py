"""
HTTP API smoke tests (FastAPI).
"""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from models.schemas import PlanningContext


@pytest.fixture
def client():
    from api.main import app

    return TestClient(app)


def test_root(client):
    r = client.get("/")
    assert r.status_code == 200
    data = r.json()
    assert "api" in data
    assert data["api"] == "/api/v1"


def test_health(client):
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_version(client):
    r = client.get("/api/v1/version")
    assert r.status_code == 200
    body = r.json()
    assert "app_name" in body
    assert "app_version" in body
    assert body["api_version"] == "1.0.0"


def test_workflow_steps(client):
    r = client.get("/api/v1/workflow/steps")
    assert r.status_code == 200
    body = r.json()
    assert len(body["steps"]) == 5
    assert body["steps"][0]["output_field"] == "travel_profile"
    assert body["steps"][-1]["output_field"] == "final_handbook"
    assert len(body["pipeline"]) == 5


def test_list_agents(client):
    r = client.get("/api/v1/agents")
    assert r.status_code == 200
    body = r.json()
    assert len(body["agents"]) == 5
    names = [a["name"] for a in body["agents"]]
    assert "User Preference Agent" in names
    assert "Cost Optimization Agent" in names


def test_plan_mocked(client):
    ctx = PlanningContext()
    ctx.metadata["user_input"] = "test"
    with patch("api.main.TravelPlanningWorkflow") as mock_wf:
        mock_wf.return_value.run.return_value = ctx
        r = client.post("/api/v1/plan", json={"user_input": "Plan a trip to Tokyo"})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert data["errors"] == []
    assert data["travel_profile"] is None


def test_plan_validation_empty(client):
    r = client.post("/api/v1/plan", json={"user_input": ""})
    assert r.status_code == 422
