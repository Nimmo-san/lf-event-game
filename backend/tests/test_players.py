import logging

from tests.factories import game_payload


def test_submit_game_success(client):
    payload = game_payload()

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
    payload = game_payload(score=100)

    first = client.post("/api/games", json=payload)
    assert first.status_code == 200

    replay = client.post("/api/games", json={**payload, "score": 99999})

    assert replay.status_code == 200
    assert replay.json()["score"] == 100


def test_submit_game_rejects_duration_beyond_round_duration_buffer(client):
    payload = game_payload(duration=135, lightning_collected=0)

    response = client.post("/api/games", json=payload)

    assert response.status_code == 400


def test_submit_game_accepts_duration_within_round_duration_buffer(client):
    # ROUND_DURATION (120s) + the jitter allowance (10s) — still under
    # the cap, so this should succeed rather than get flagged as an
    # impossible round length.
    payload = game_payload(duration=125, lightning_collected=0)

    response = client.post("/api/games", json=payload)

    assert response.status_code == 200


def test_submit_game_rejects_score_over_max(client):
    payload = game_payload(score=100_001)

    response = client.post("/api/games", json=payload)

    assert response.status_code == 400


def test_submit_game_rejects_lightning_over_max(client):
    payload = game_payload(lightning_collected=1_001)

    response = client.post("/api/games", json=payload)

    assert response.status_code == 400


def test_submit_game_rejects_non_positive_duration_at_schema_level(client):
    """Field(gt=0) on GameResultCreate.duration rejects this before the
    route body even runs — so it's a 422 (schema validation), not the
    400 the route's own `duration <= 0` check would raise. That check
    is effectively unreachable dead code; documenting the actual
    behavior here rather than the presumably-intended one.
    """
    payload = game_payload(duration=0, lightning_collected=0)

    response = client.post("/api/games", json=payload)

    assert response.status_code == 422


def test_submit_game_rejects_company_name_that_looks_like_a_website(client):
    payload = game_payload(company_name="acme.com")

    response = client.post("/api/games", json=payload)

    assert response.status_code == 422


def test_submit_game_rejects_player_name_that_looks_like_an_email(client):
    payload = game_payload(player_name="jordan@example.com")

    response = client.post("/api/games", json=payload)

    assert response.status_code == 422


def test_submit_game_rejects_score_implausible_for_duration_and_lightning(client):
    """A game_payload() score is always exactly the ceiling for its
    duration/lightning — bumping it past that ceiling is what a forged
    submission (e.g. a direct API call skipping the game entirely)
    would look like.
    """
    payload = game_payload(duration=10, lightning_collected=0, score=5_000)

    response = client.post("/api/games", json=payload)

    assert response.status_code == 400


def test_submit_game_rejects_implausible_score_logs_a_warning(client, caplog):
    payload = game_payload(duration=10, lightning_collected=0, score=5_000)

    with caplog.at_level(logging.WARNING, logger="app.routes.players"):
        client.post("/api/games", json=payload)

    assert "Rejected game submission" in caplog.text


def test_submit_game_accepts_score_at_plausible_ceiling(client):
    # game_payload()'s default score is already exactly this ceiling —
    # asserted explicitly here so the boundary itself is under test,
    # not just incidentally exercised by every other test using it.
    payload = game_payload(duration=30, lightning_collected=5)

    response = client.post("/api/games", json=payload)

    assert response.status_code == 200
