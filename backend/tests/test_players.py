import uuid


def _game_payload(**overrides):
    payload = {
        "game_id": str(uuid.uuid4()),
        "player_id": str(uuid.uuid4()),
        "player_name": "Jordan Lee",
        "company_name": "Acme Corp",
        "score": 4200,
        "lightning_collected": 12,
        "duration": 45.5,
    }

    payload.update(overrides)

    return payload


def test_submit_game_success(client):
    payload = _game_payload()

    response = client.post("/api/games", json=payload)

    assert response.status_code == 200

    body = response.json()

    assert body["game_id"] == payload["game_id"]
    assert body["player_id"] == payload["player_id"]
    assert body["score"] == payload["score"]
    assert body["lightning_collected"] == payload["lightning_collected"]


def test_submit_game_is_idempotent_on_replay(client):
    """A retried submission (e.g. a flaky-wifi sync retry) for the same
    game_id must return the original result, not create a second row or
    let a replayed/edited payload overwrite it.
    """
    payload = _game_payload(score=100)

    first = client.post("/api/games", json=payload)
    assert first.status_code == 200

    replay = client.post("/api/games", json={**payload, "score": 99999})

    assert replay.status_code == 200
    assert replay.json()["score"] == 100


def test_submit_game_rejects_duration_over_max(client):
    payload = _game_payload(duration=301)

    response = client.post("/api/games", json=payload)

    assert response.status_code == 400


def test_submit_game_rejects_score_over_max(client):
    payload = _game_payload(score=100_001)

    response = client.post("/api/games", json=payload)

    assert response.status_code == 400


def test_submit_game_rejects_lightning_over_max(client):
    payload = _game_payload(lightning_collected=1_001)

    response = client.post("/api/games", json=payload)

    assert response.status_code == 400


def test_submit_game_rejects_non_positive_duration_at_schema_level(client):
    """Field(gt=0) on GameResultCreate.duration rejects this before the
    route body even runs — so it's a 422 (schema validation), not the
    400 the route's own `duration <= 0` check would raise. That check
    is effectively unreachable dead code; documenting the actual
    behavior here rather than the presumably-intended one.
    """
    payload = _game_payload(duration=0)

    response = client.post("/api/games", json=payload)

    assert response.status_code == 422


def test_submit_game_rejects_company_name_that_looks_like_a_website(client):
    payload = _game_payload(company_name="acme.com")

    response = client.post("/api/games", json=payload)

    assert response.status_code == 422


def test_submit_game_rejects_player_name_that_looks_like_an_email(client):
    payload = _game_payload(player_name="jordan@example.com")

    response = client.post("/api/games", json=payload)

    assert response.status_code == 422
