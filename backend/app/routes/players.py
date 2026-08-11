from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request

from sqlalchemy.orm import Session

from app.rate_limit import limiter

from app.database import get_db
from app.models.game import GameResult
from app.schemas.player import GameResultResponse, GameResultCreate


router = APIRouter(
    prefix="/api",
    tags=["Game"],
)


@router.post(
    "/games",
    response_model=GameResultResponse,
)
@limiter.limit("20/minute")
def submit_game(
    request: Request,
    payload: GameResultCreate,
    db: Session = Depends(get_db),
):

    existing_game = db.get(
        GameResult,
        payload.game_id,
    )

    if existing_game:
        return {
            "game_id": existing_game.id,
            "player_id": existing_game.player_id,
            "player_name": existing_game.player_name,
            "company_name": existing_game.company_name,
            "score": existing_game.score,
            "lightning_collected": (existing_game.lightning_collected),
            "duration": existing_game.duration,
            "created_at": existing_game.created_at,
        }

    # if duration of game is less than 0
    if payload.duration <= 0:
        raise HTTPException(
            status_code=400,
            detail="Invalid duration.",
        )

    # if duration is higher
    if payload.duration > 300:
        raise HTTPException(
            status_code=400,
            detail="Invalid duration.",
        )

    # if score is higher than 100000, needs to change TODO
    if payload.score > 100_000:
        raise HTTPException(
            status_code=400,
            detail="Invalid score.",
        )

    # if lightning collected is higher than 1000, needs to change TODO
    if payload.lightning_collected > 1_000:
        raise HTTPException(
            status_code=400,
            detail="Invalid lightning count.",
        )

    game = GameResult(
        id=payload.game_id,
        player_id=payload.player_id,
        player_name=payload.player_name.strip(),
        company_name=payload.company_name.strip(),
        # email=str(payload.email),
        score=payload.score,
        lightning_collected=(payload.lightning_collected),
        duration=payload.duration,
    )

    db.add(game)

    db.commit()

    db.refresh(game)

    return {
        "game_id": game.id,
        "player_id": game.player_id,
        "player_name": game.player_name,
        "company_name": game.company_name,
        "score": game.score,
        "lightning_collected": (game.lightning_collected),
        "duration": game.duration,
        "created_at": game.created_at,
    }
