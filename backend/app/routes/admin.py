import csv
import io
import logging
import os
import secrets
import hashlib
import uuid

from datetime import datetime, timezone, timedelta

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Request,
    Response,
)

from fastapi.responses import StreamingResponse

from pydantic import BaseModel, Field

from sqlalchemy import or_, func
from sqlalchemy.orm import Session

from app.models.admin import AdminSession
from app.database import get_db
from app.models.game import GameResult
from app.models.leaderboard import LeaderboardEntry
from app.rate_limit import limiter
from app.schemas.player import MarketingExportRequest


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/admin",
    tags=["Admin"],
)


ADMIN_EXPORT_KEY = os.environ.get(
    "ADMIN_EXPORT_KEY",
)

ADMIN_COOKIE = "lightning_admin_session"

SESSION_DURATION_HOURS = 4

IS_PRODUCTION = os.environ.get("ENVIRONMENT") == "production"


class AdminLoginRequest(BaseModel):
    key: str = Field(
        min_length=8,
        max_length=256,
    )


def require_admin(
    request: Request,
    db: Session = Depends(get_db),
):

    raw_token = request.cookies.get(
        ADMIN_COOKIE,
    )

    if not raw_token:
        raise HTTPException(
            status_code=401,
            detail="Admin authentication required.",
        )

    token_hash = hash_session_token(
        raw_token,
    )

    session = (
        db.query(AdminSession).filter(AdminSession.token_hash == token_hash).first()
    )

    if not session:
        raise HTTPException(
            status_code=401,
            detail="Invalid admin session.",
        )

    now = datetime.now(timezone.utc)

    expires_at = session.expires_at

    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(
            tzinfo=timezone.utc,
        )

    if expires_at <= now:
        db.delete(session)
        db.commit()

        raise HTTPException(status_code=401, detail="Admin session expired.")

    return session


def admin_key_matches(
    key: str,
) -> bool:
    if not ADMIN_EXPORT_KEY:
        return False

    return secrets.compare_digest(
        key.encode("utf-8"),
        ADMIN_EXPORT_KEY.encode("utf-8"),
    )


def hash_session_token(
    token: str,
) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


@router.get("/session")
def admin_session(
    _: AdminSession = Depends(
        require_admin,
    ),
):
    return {
        "authenticated": True,
    }


@router.post("/login")
@limiter.limit("5/minute")
def admin_login(
    request: Request,
    payload: AdminLoginRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    if not admin_key_matches(
        payload.key,
    ):
        logger.warning(
            "Admin login failed: invalid key (ip=%s)",
            _client_ip(request),
        )
        raise HTTPException(
            status_code=401,
            detail="Invalid admin key.",
        )

    # token generation
    raw_token = secrets.token_urlsafe(32)

    token_hash = hash_session_token(raw_token)

    now = datetime.now(timezone.utc)

    expires_at = now + timedelta(
        hours=SESSION_DURATION_HOURS,
    )

    session = AdminSession(
        id=str(uuid.uuid4()),
        token_hash=token_hash,
        created_at=now,
        expires_at=expires_at,
    )

    # add session to db
    db.add(session)
    db.commit()

    response.set_cookie(
        key=ADMIN_COOKIE,
        value=raw_token,
        httponly=True,
        secure=IS_PRODUCTION,
        samesite="none",  # different frontend site, otherwise its "strict"
        max_age=60 * 60 * SESSION_DURATION_HOURS,
        path="/",
    )

    logger.info(
        "Admin login succeeded (ip=%s)",
        _client_ip(request),
    )

    return {"authenticated": True, "expires_at": expires_at}


@router.post("/logout")
def admin_logout(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):

    raw_token = request.cookies.get(
        ADMIN_COOKIE,
    )

    if raw_token:
        token_hash = hash_session_token(
            raw_token,
        )

        session = (
            db.query(AdminSession).filter(AdminSession.token_hash == token_hash).first()
        )

        if session:
            db.delete(session)
            db.commit()

            logger.info(
                "Admin logout (ip=%s)",
                _client_ip(request),
            )

    response.delete_cookie(
        key=ADMIN_COOKIE,
        path="/",
    )

    return {
        "authenticated": False,
    }


@router.get("/entries")
@limiter.limit("60/minute")
def get_admin_entries(
    request: Request,
    search: str | None = Query(
        default=None,
        max_length=150,
    ),
    name: str | None = Query(
        default=None,
        max_length=100,
    ),
    email: str | None = Query(
        default=None,
        max_length=255,
    ),
    db: Session = Depends(get_db),
    _: AdminSession = Depends(
        require_admin,
    ),
):
    # Rank every leaderboard entry belonging to the
    # same email address.
    # Rank 1 = that email's best-scoring submission.
    # lower(email) ensures:
    # John@Example.com
    # john@example.com
    # are treated as the same contact.
    ranked_entries = db.query(
        LeaderboardEntry.id,
        LeaderboardEntry.email,
        LeaderboardEntry.created_at,
        GameResult.player_name,
        GameResult.score,
        GameResult.lightning_collected,
        func.row_number()
        .over(
            partition_by=func.lower(
                LeaderboardEntry.email,
            ),
            order_by=(
                GameResult.score.desc(),
                LeaderboardEntry.created_at.asc(),
            ),
        )
        .label("email_rank"),
    ).join(
        GameResult,
        GameResult.id == LeaderboardEntry.game_id,
    )

    # Apply filters before deduplication.
    # This means the unique-contact result is
    # calculated from the records matching the
    # current admin filters.
    if search:
        value = f"%{search.strip()}%"

        ranked_entries = ranked_entries.filter(
            or_(
                GameResult.player_name.ilike(
                    value,
                ),
                LeaderboardEntry.email.ilike(
                    value,
                ),
            )
        )

    if name:
        ranked_entries = ranked_entries.filter(
            GameResult.player_name.ilike(f"%{name.strip()}%")
        )

    if email:
        ranked_entries = ranked_entries.filter(
            LeaderboardEntry.email.ilike(f"%{email.strip()}%")
        )

    # Turn the ranked query into a subquery so we
    # can select only rank 1 for each email.
    ranked_entries = ranked_entries.subquery()

    rows = (
        db.query(
            ranked_entries,
        )
        .filter(
            ranked_entries.c.email_rank == 1,
        )
        .order_by(
            ranked_entries.c.created_at.desc(),
        )
        .limit(500)
        .all()
    )

    return [
        {
            "id": row.id,
            "email": row.email,
            "player_name": row.player_name,
            "score": row.score,
            "lightning_collected": row.lightning_collected,
            "entered_at": row.created_at,
        }
        for row in rows
    ]


@router.post("/export/marketing")
@limiter.limit("10/minute")
def export_marketing_data(
    request: Request,
    payload: MarketingExportRequest,
    db: Session = Depends(get_db),
    _: AdminSession = Depends(require_admin),
):
    ranked_entries = db.query(
        LeaderboardEntry.id,
        LeaderboardEntry.email,
        LeaderboardEntry.created_at,
        GameResult.player_name,
        func.row_number()
        .over(
            partition_by=func.lower(LeaderboardEntry.email),
            order_by=LeaderboardEntry.created_at.asc(),
        )
        .label("email_rank"),
    ).join(
        GameResult,
        GameResult.id == LeaderboardEntry.game_id,
    )

    if payload.search:
        value = f"%{payload.search.strip()}%"

        ranked_entries = ranked_entries.filter(
            or_(
                GameResult.player_name.ilike(value),
                LeaderboardEntry.email.ilike(value),
            )
        )

    if payload.name:
        ranked_entries = ranked_entries.filter(
            GameResult.player_name.ilike(f"%{payload.name.strip()}%")
        )

    if payload.email:
        ranked_entries = ranked_entries.filter(
            LeaderboardEntry.email.ilike(f"%{payload.email.strip()}%")
        )

    if payload.excluded_ids:
        ranked_entries = ranked_entries.filter(
            ~LeaderboardEntry.id.in_(
                payload.excluded_ids,
            )
        )

    ranked_entries = ranked_entries.subquery()

    rows = (
        db.query(ranked_entries)
        .filter(ranked_entries.c.email_rank == 1)
        .order_by(ranked_entries.c.created_at.asc())
        .all()
    )

    output = io.StringIO()

    writer = csv.writer(output)

    writer.writerow(
        [
            "email",
            "player_name",
            "entered_at",
        ]
    )

    for row in rows:
        writer.writerow(
            [
                row.email,
                row.player_name,
                row.created_at.isoformat(),
            ]
        )

    output.seek(0)

    return StreamingResponse(
        iter(
            [
                output.getvalue(),
            ]
        ),
        media_type="text/csv",
        headers={
            "Content-Disposition": 'attachment; filename="lightning-flight-marketing.csv"',
            "Cache-Control": "no-store",
        },
    )


@router.get("/analytics")
@limiter.limit("30/minute")
def get_admin_analytics(
    request: Request,
    db: Session = Depends(get_db),
    _: AdminSession = Depends(require_admin),
):
    total_games = db.query(func.count(GameResult.id)).scalar() or 0

    unique_players = (
        db.query(func.count(func.distinct(GameResult.player_id))).scalar() or 0
    )

    repeat_players = (
        db.query(GameResult.player_id)
        .group_by(GameResult.player_id)
        .having(func.count(GameResult.id) > 1)
        .count()
    )

    average_score = db.query(func.avg(GameResult.score)).scalar() or 0

    highest_score = db.query(func.max(GameResult.score)).scalar() or 0

    average_lightning = db.query(func.avg(GameResult.lightning_collected)).scalar() or 0

    average_duration = db.query(func.avg(GameResult.duration)).scalar() or 0

    # Unique leaderboard contacts.
    # Email is used here because the admin marketing
    # view is also deduplicated by email.
    unique_leaderboard_entries = (
        db.query(func.count(func.distinct(func.lower(LeaderboardEntry.email)))).scalar()
        or 0
    )

    average_games_per_player = total_games / unique_players if unique_players else 0

    replay_rate = repeat_players / unique_players * 100 if unique_players else 0

    leaderboard_conversion_rate = (
        unique_leaderboard_entries / unique_players * 100 if unique_players else 0
    )

    games_over_time_rows = (
        db.query(
            func.strftime(
                "%Y-%m-%d %H:00",
                GameResult.created_at,
            ).label("period"),
            func.count(GameResult.id).label("games"),
        )
        .group_by(
            "period",
        )
        .order_by(
            "period",
        )
        .all()
    )

    # simple score distribution bucket
    score_buckets = [
        (0, 999),
        (1000, 1999),
        (2000, 2999),
        (3000, 3999),
        (4000, 4999),
        (5000, 5999),
        (6000, 999999),
    ]

    score_distribution = []

    for minimum, maximum in score_buckets:
        count = (
            db.query(func.count(GameResult.id))
            .filter(
                GameResult.score >= minimum,
                GameResult.score <= maximum,
            )
            .scalar()
            or 0
        )

        label = f"{minimum:,}+" if maximum >= 999999 else f"{minimum:,}-{maximum:,}"

        score_distribution.append(
            {
                "label": label,
                "minimum": minimum,
                "maximum": maximum,
                "games": count,
            }
        )

    games_per_player_subquery = (
        db.query(
            GameResult.player_id,
            func.count(GameResult.id).label("game_count"),
        )
        .group_by(
            GameResult.player_id,
        )
        .subquery()
    )

    games_per_player_rows = (
        db.query(
            games_per_player_subquery.c.game_count,
            func.count().label("players"),
        )
        .group_by(
            games_per_player_subquery.c.game_count,
        )
        .order_by(
            games_per_player_subquery.c.game_count,
        )
        .all()
    )

    return {
        "players": {
            "unique_players": unique_players,
            "total_games": total_games,
            "repeat_players": repeat_players,
            "average_games_per_player": round(
                average_games_per_player,
                2,
            ),
            "replay_rate": round(
                replay_rate,
                2,
            ),
        },
        "gameplay": {
            "average_score": round(
                float(average_score),
                2,
            ),
            "highest_score": highest_score,
            "average_lightning": round(
                float(average_lightning),
                2,
            ),
            "average_duration": round(
                float(average_duration),
                2,
            ),
        },
        "leaderboard": {
            "unique_entries": unique_leaderboard_entries,
            "conversion_rate": round(
                leaderboard_conversion_rate,
                2,
            ),
        },
        "activity": {
            "games_over_time": [
                {
                    "period": row.period,
                    "games": row.games,
                }
                for row in games_over_time_rows
            ],
        },
        "distributions": {
            "scores": score_distribution,
            "games_per_player": [
                {
                    "games": row.game_count,
                    "players": row.players,
                }
                for row in games_per_player_rows
            ],
        },
    }
