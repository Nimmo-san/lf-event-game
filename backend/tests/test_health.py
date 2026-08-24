from app.database import get_db
from app.main import app


def test_health_ok(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "lightning-flight-api",
    }


def test_health_returns_503_when_db_unreachable(client):
    class _BrokenSession:
        def execute(self, *args, **kwargs):
            raise RuntimeError("simulated DB failure")

        def close(self):
            pass

    def _broken_get_db():
        yield _BrokenSession()

    app.dependency_overrides[get_db] = _broken_get_db

    try:
        response = client.get("/health")
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 503
