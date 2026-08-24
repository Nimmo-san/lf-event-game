import uuid

from app.scoring import max_plausible_score


def game_payload(*, duration: float = 45.5, lightning_collected: int = 12, **overrides) -> dict:
    """A POST /api/games payload that's internally consistent by
    construction — `score` defaults to the exact ceiling
    `max_plausible_score` allows for the given duration/lightning, so
    callers who only care about some other field never have to worry
    about accidentally tripping the plausibility check with an
    arbitrary hardcoded score.
    """
    payload = {
        "game_id": str(uuid.uuid4()),
        "player_id": str(uuid.uuid4()),
        "player_name": "Jordan Lee",
        "lightning_collected": lightning_collected,
        "duration": duration,
        "score": round(max_plausible_score(duration, lightning_collected)),
    }

    payload.update(overrides)

    return payload
