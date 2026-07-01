"""API tests for the Sentiment API service.

Uses FastAPI's TestClient, which runs the app in-process - no server
needed, no network. Fast and deterministic, which is what CI wants.
"""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_predict_positive_text():
    response = client.post("/predict", json={"text": "I love this, it's wonderful"})
    assert response.status_code == 200
    body = response.json()
    assert body["label"] == "positive"
    assert 0.0 <= body["confidence"] <= 1.0


def test_predict_negative_text():
    response = client.post("/predict", json={"text": "This is awful and terrible"})
    assert response.status_code == 200
    assert response.json()["label"] == "negative"


def test_predict_rejects_empty_text():
    """Pydantic should reject empty input with a 422, no handler code needed."""
    response = client.post("/predict", json={"text": ""})
    assert response.status_code == 422


def test_predict_rejects_missing_field():
    response = client.post("/predict", json={})
    assert response.status_code == 422