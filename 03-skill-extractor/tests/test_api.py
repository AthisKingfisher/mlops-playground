"""API tests for the skill-extractor service."""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_extract_finds_known_skills():
    response = client.post("/extract", json={"text": "I use Python and Docker daily"})
    assert response.status_code == 200
    body = response.json()
    skills = {s["skill"] for s in body["skills"]}
    assert "Python" in skills
    assert "Docker" in skills
    assert body["count"] == len(body["skills"])


def test_extract_resolves_alias():
    """'Postgres' should resolve to the canonical 'PostgreSQL'."""
    response = client.post("/extract", json={"text": "experienced with Postgres"})
    skills = {s["skill"] for s in response.json()["skills"]}
    assert "PostgreSQL" in skills


def test_extract_catches_typo_via_fuzzy():
    """'kubernets' should fuzzy-match Kubernetes (scores ~94, above threshold 88)."""
    response = client.post("/extract", json={"text": "deployed with kubernets"})
    results = response.json()["skills"]
    kube = [s for s in results if s["skill"] == "Kubernetes"]
    assert len(kube) == 1
    assert kube[0]["match"] == "fuzzy"


def test_does_not_confuse_java_and_javascript():
    """The word-boundary guardrail: Java must not match inside JavaScript."""
    response = client.post("/extract", json={"text": "I know JavaScript well"})
    skills = {s["skill"] for s in response.json()["skills"]}
    assert "JavaScript" in skills
    assert "Java" not in skills


def test_extract_rejects_empty_text():
    response = client.post("/extract", json={"text": ""})
    assert response.status_code == 422