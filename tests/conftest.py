import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def test_experiment_data():
    return {
        "name": "test_experiment",
        "database_type": "postgres",
        "config": {
            "rows": 100,
            "concurrent_queries": 5
        }
    }

