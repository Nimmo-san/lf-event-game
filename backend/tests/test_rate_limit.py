def _login_attempt(client, forwarded_for: str):
    return client.post(
        "/api/admin/login",
        json={"key": "definitely-the-wrong-key"},
        headers={"X-Forwarded-For": forwarded_for},
    )


def test_rate_limit_is_scoped_per_forwarded_for_ip(client):
    """/api/admin/login is limited to 5/minute. Before the fix,
    get_remote_address read request.client.host, which is the same
    value for every request through FastAPI's TestClient (and, in
    production, the same value for every visitor — Render's own
    proxy IP, since the backend runs plain uvicorn with no
    --proxy-headers flag). That collapsed every distinct visitor into
    one shared rate-limit bucket.

    This drives 5 attempts under one X-Forwarded-For value to exhaust
    its budget, then confirms a *different* X-Forwarded-For value
    still gets through — proving the limiter is keying off the
    forwarded IP, not the shared underlying connection.
    """
    for _ in range(5):
        response = _login_attempt(client, "203.0.113.10")
        assert response.status_code == 401

    exhausted = _login_attempt(client, "203.0.113.10")
    assert exhausted.status_code == 429

    different_visitor = _login_attempt(client, "203.0.113.99")
    assert different_visitor.status_code == 401
