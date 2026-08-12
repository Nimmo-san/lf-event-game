import uuid

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request

from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from app.rate_limit import limiter
from app.database import get_db
from app.models.game import GameResult
from app.models.leaderboard import LeaderboardEntry
from app.schemas.player import (
    LeaderboardRow,
    LeaderboardEntryCreate,
    LeaderboardEntryResponse,
    PlayerRankResponse,
)


router = APIRouter(
    prefix="/api",
    tags=["Leaderboard"],
)


@router.post(
    "/leaderboard/entries",
    response_model=LeaderboardEntryResponse,
)
@limiter.limit("10/minute")
def submit_leaderboard_entry(
    request: Request,
    payload: LeaderboardEntryCreate,
    db: Session = Depends(get_db),
):

    game = db.get(
        GameResult,
        payload.game_id,
    )

    if not game:
        raise HTTPException(
            status_code=404,
            detail="Game result not found.",
        )

    if game.player_id != payload.player_id:
        raise HTTPException(
            status_code=403,
            detail="Game does not belong to player.",
        )

    existing_entry = (
        db.query(LeaderboardEntry)
        .filter(LeaderboardEntry.game_id == payload.game_id)
        .first()
    )

    if existing_entry:
        raise HTTPException(
            status_code=409,
            detail="This game has already been submitted.",
        )

    entry = LeaderboardEntry(
        id=str(uuid.uuid4()),
        game_id=game.id,
        player_id=game.player_id,
        email=str(payload.email),
        # marketing_consent=payload.marketing_consent,
    )

    db.add(entry)

    db.commit()

    rank = calculate_player_rank(
        db,
        game.player_id,
    )

    return {
        "success": True,
        "game_id": game.id,
        "player_id": game.player_id,
        "score": game.score,
        "rank": rank,
    }


@router.get(
    "/leaderboard",
    response_model=list[LeaderboardRow],
)
@limiter.limit("60/minute")
def get_leaderboard(
    request: Request,
    db: Session = Depends(get_db),
):
    ranked_games = build_best_submitted_games_query(
        db,
    )

    top_players = (
        db.query(
            ranked_games.c.player_id,
            ranked_games.c.player_name,
            ranked_games.c.company_name,
            ranked_games.c.score,
            ranked_games.c.lightning_collected,
        )
        .filter(
            ranked_games.c.player_game_rank == 1,
        )
        .order_by(
            ranked_games.c.score.desc(),
            ranked_games.c.created_at.asc(),
            ranked_games.c.player_name.asc(),
        )
        .limit(10)
        .all()
    )

    return [
        {
            "rank": rank,
            "player_name": player.player_name,
            "company_name": player.company_name,
            "score": player.score,
            "lightning_collected": player.lightning_collected,
        }
        for rank, player in enumerate(
            top_players,
            start=1,
        )
    ]


@router.get(
    "/leaderboard/rank/{player_id}",
    response_model=PlayerRankResponse,
)
@limiter.limit("60/minute")
def get_player_rank(
    request: Request,
    player_id: str,
    db: Session = Depends(get_db),
):
    ranked_games = build_best_submitted_games_query(
        db,
    )

    best_players = (
        db.query(
            ranked_games.c.player_id,
            ranked_games.c.score,
            ranked_games.c.created_at,
            ranked_games.c.player_name,
        )
        .filter(
            ranked_games.c.player_game_rank == 1,
        )
        .order_by(
            ranked_games.c.score.desc(),
            ranked_games.c.created_at.asc(),
            ranked_games.c.player_name.asc(),
        )
        .all()
    )

    for rank, player in enumerate(
        best_players,
        start=1,
    ):
        if player.player_id == player_id:
            return {
                "player_id": player.player_id,
                "rank": rank,
                "score": player.score,
            }

    raise HTTPException(
        status_code=404,
        detail="Player is not on the leaderboard.",
    )


def calculate_player_rank(
    db: Session,
    player_id: str,
    ) -> int:
    ranked_games = build_best_submitted_games_query(
        db,
    )

    players = (
        db.query(
            ranked_games.c.player_id,
        )
        .filter(
            ranked_games.c.player_game_rank == 1,
        )
        .order_by(
            ranked_games.c.score.desc(),
            ranked_games.c.created_at.asc(),
            ranked_games.c.player_name.asc(),
        )
        .all()
    )

    for rank, player in enumerate(
        players,
        start=1,
    ):
        if player.player_id == player_id:
            return rank

    raise HTTPException(
        status_code=404,
        detail="Player rank not found.",
    )


def build_best_submitted_games_query(
    db: Session,
):
    ranked_games = (
        db.query(
            LeaderboardEntry.player_id,
            GameResult.id.label("game_id"),
            GameResult.player_name,
            GameResult.company_name,
            GameResult.score,
            GameResult.lightning_collected,
            GameResult.created_at,
            func.row_number()
            .over(
                partition_by=LeaderboardEntry.player_id,
                order_by=(
                    GameResult.score.desc(),
                    GameResult.created_at.asc(),
                ),
            )
            .label("player_game_rank"),
        )
        .join(
            GameResult,
            GameResult.id == LeaderboardEntry.game_id,
        )
        .subquery()
    )

    return ranked_games
