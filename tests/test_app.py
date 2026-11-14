from fastapi.testclient import TestClient

from burn.app import app


def test_health():
    assert TestClient(app).get("/api/health").json() == {"status": "ok"}
