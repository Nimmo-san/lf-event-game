import logging

from tests.conftest import TEST_ADMIN_EXPORT_KEY


def test_admin_login_rejects_wrong_key(client):
    response = client.post(
        "/api/admin/login",
        json={"key": "definitely-the-wrong-key"},
    )

    assert response.status_code == 401


def test_admin_login_logs_failed_attempt(client, caplog):
    with caplog.at_level(logging.WARNING, logger="app.routes.admin"):
        client.post(
            "/api/admin/login",
            json={"key": "definitely-the-wrong-key"},
        )

    assert "Admin login failed" in caplog.text


def test_admin_login_succeeds_and_sets_cookie(client):
    response = client.post(
        "/api/admin/login",
        json={"key": TEST_ADMIN_EXPORT_KEY},
    )

    assert response.status_code == 200
    assert response.json()["authenticated"] is True
    assert "lightning_admin_session" in response.cookies


def test_admin_login_logs_success(client, caplog):
    with caplog.at_level(logging.INFO, logger="app.routes.admin"):
        client.post(
            "/api/admin/login",
            json={"key": TEST_ADMIN_EXPORT_KEY},
        )

    assert "Admin login succeeded" in caplog.text


def test_admin_session_requires_auth(client):
    response = client.get("/api/admin/session")

    assert response.status_code == 401


def test_admin_session_succeeds_after_login(client):
    client.post("/api/admin/login", json={"key": TEST_ADMIN_EXPORT_KEY})

    response = client.get("/api/admin/session")

    assert response.status_code == 200
    assert response.json() == {"authenticated": True}


def test_admin_logout_clears_session(client):
    client.post("/api/admin/login", json={"key": TEST_ADMIN_EXPORT_KEY})

    logout_response = client.post("/api/admin/logout")
    assert logout_response.status_code == 200

    session_response = client.get("/api/admin/session")
    assert session_response.status_code == 401
