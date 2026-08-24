import uuid


def _submit_game(client, **overrides):
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

    response = client.post("/api/games", json=payload)
    assert response.status_code == 200

    return payload


def test_submit_leaderboard_entry_success(client):
    game = _submit_game(client)

    response = client.post(
        "/api/leaderboard/entries",
        json={
            "game_id": game["game_id"],
            "player_id": game["player_id"],
            "email": "jordan@example.com",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["rank"] == 1


def test_submit_leaderboard_entry_unknown_game_returns_404(client):
    response = client.post(
        "/api/leaderboard/entries",
        json={
            "game_id": str(uuid.uuid4()),
            "player_id": str(uuid.uuid4()),
            "email": "jordan@example.com",
        },
    )

    assert response.status_code == 404


def test_submit_leaderboard_entry_player_mismatch_returns_403(client):
    game = _submit_game(client)

    response = client.post(
        "/api/leaderboard/entries",
        json={
            "game_id": game["game_id"],
            "player_id": str(uuid.uuid4()),
            "email": "jordan@example.com",
        },
    )

    assert response.status_code == 403


def test_submit_leaderboard_entry_duplicate_returns_409(client):
    game = _submit_game(client)

    entry_payload = {
        "game_id": game["game_id"],
        "player_id": game["player_id"],
        "email": "jordan@example.com",
    }

    first = client.post("/api/leaderboard/entries", json=entry_payload)
    assert first.status_code == 200

    duplicate = client.post("/api/leaderboard/entries", json=entry_payload)

    assert duplicate.status_code == 409


def test_get_leaderboard_ranks_best_score_per_player_first(client):
    game_a = _submit_game(client, score=500)
    game_b = _submit_game(client, score=9000)

    for game in (game_a, game_b):
        client.post(
            "/api/leaderboard/entries",
            json={
                "game_id": game["game_id"],
                "player_id": game["player_id"],
                "email": f"{game['player_id']}@example.com",
            },
        )

    response = client.get("/api/leaderboard")

    assert response.status_code == 200

    rows = response.json()

    assert rows[0]["player_id"] == game_b["player_id"]
    assert rows[0]["rank"] == 1


def test_get_player_rank_for_unknown_player_returns_404(client):
    response = client.get(f"/api/leaderboard/rank/{uuid.uuid4()}")

    assert response.status_code == 404


def test_get_player_rank_success(client):
    game = _submit_game(client)

    client.post(
        "/api/leaderboard/entries",
        json={
            "game_id": game["game_id"],
            "player_id": game["player_id"],
            "email": "jordan@example.com",
        },
    )

    response = client.get(f"/api/leaderboard/rank/{game['player_id']}")

    assert response.status_code == 200
    assert response.json() == {
        "player_id": game["player_id"],
        "rank": 1,
        "score": game["score"],
    }
