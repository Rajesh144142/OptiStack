import pytest
from fastapi.testclient import TestClient

def test_create_experiment(client: TestClient, test_experiment_data):
    response = client.post("/api/v1/experiments/", json=test_experiment_data)
    assert response.status_code == 200
    assert response.json()["name"] == test_experiment_data["name"]

def test_list_experiments(client: TestClient):
    response = client.get("/api/v1/experiments/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

