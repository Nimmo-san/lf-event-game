import csv
import io
import os
import secrets

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Request,
    Response,
)

from fastapi.responses import StreamingResponse

from pydantic import BaseModel

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.game import GameResult
from app.models.leaderboard import LeaderboardEntry
from app.rate_limit import limiter


router = APIRouter(
    prefix="/api/admin",
    tags=["Admin"],
)


ADMIN_EXPORT_KEY = os.environ.get(
    "ADMIN_EXPORT_KEY",
)

ADMIN_COOKIE = "lightning_admin"

IS_PRODUCTION = os.environ.get("ENVIRONMENT") == "production"


class AdminLoginRequest(BaseModel):
    key: str


def require_admin(
    request: Request,
):
    cookie = request.cookies.get(
        ADMIN_COOKIE,
    )

    if (
        not ADMIN_EXPORT_KEY
        or not cookie
        or not secrets.compare_digest(
            cookie,
            ADMIN_EXPORT_KEY,
        )
    ):
        raise HTTPException(
            status_code=401,
            detail="Admin authentication required.",
        )


@router.post("/login")
@limiter.limit("5/minute")
def admin_login(
    request: Request,
    payload: AdminLoginRequest,
    response: Response,
):
    if not ADMIN_EXPORT_KEY or not secrets.compare_digest(
        payload.key,
        ADMIN_EXPORT_KEY,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid admin key.",
        )

    response.set_cookie(
        key=ADMIN_COOKIE,
        value=ADMIN_EXPORT_KEY,
        httponly=True,
        secure=IS_PRODUCTION,
        samesite="strict",
        max_age=60 * 60 * 4,
        path="/",
    )

    return {
        "authenticated": True,
    }


@router.post("/logout")
def admin_logout(
    response: Response,
):
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
    company: str | None = Query(
        default=None,
        max_length=150,
    ),
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
):
    query = db.query(
        LeaderboardEntry.id,
        LeaderboardEntry.email,
        LeaderboardEntry.created_at,
        GameResult.player_name,
        GameResult.company_name,
        GameResult.score,
        GameResult.lightning_collected,
    ).join(
        GameResult,
        GameResult.id == LeaderboardEntry.game_id,
    )

    if search:
        value = f"%{search.strip()}%"

        query = query.filter(
            or_(
                GameResult.player_name.ilike(value),
                GameResult.company_name.ilike(value),
                LeaderboardEntry.email.ilike(value),
            )
        )

    if name:
        query = query.filter(GameResult.player_name.ilike(f"%{name.strip()}%"))

    if email:
        query = query.filter(LeaderboardEntry.email.ilike(f"%{email.strip()}%"))

    if company:
        query = query.filter(GameResult.company_name.ilike(f"%{company.strip()}%"))

    rows = (
        query.order_by(
            LeaderboardEntry.created_at.desc(),
        )
        .limit(500)
        .all()
    )

    return [
        {
            "id": row.id,
            "email": row.email,
            "player_name": row.player_name,
            "company_name": row.company_name,
            "score": row.score,
            "lightning_collected": row.lightning_collected,
            "entered_at": row.created_at,
        }
        for row in rows
    ]


@router.get("/export/marketing")
@limiter.limit("10/minute")
def export_marketing_data(
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
    company: str | None = Query(
        default=None,
        max_length=150,
    ),
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
):
    query = db.query(
        LeaderboardEntry.email,
        LeaderboardEntry.created_at,
        GameResult.player_name,
        GameResult.company_name,
    ).join(
        GameResult,
        GameResult.id == LeaderboardEntry.game_id,
    )

    if search:
        value = f"%{search.strip()}%"

        query = query.filter(
            or_(
                GameResult.player_name.ilike(value),
                GameResult.company_name.ilike(value),
                LeaderboardEntry.email.ilike(value),
            )
        )

    if name:
        query = query.filter(GameResult.player_name.ilike(f"%{name.strip()}%"))

    if email:
        query = query.filter(LeaderboardEntry.email.ilike(f"%{email.strip()}%"))

    if company:
        query = query.filter(GameResult.company_name.ilike(f"%{company.strip()}%"))

    rows = query.order_by(
        LeaderboardEntry.created_at.asc(),
    ).all()

    output = io.StringIO()

    writer = csv.writer(
        output,
    )

    writer.writerow(
        [
            "email",
            "player_name",
            "company_name",
            "entered_at",
        ]
    )

    for row in rows:
        writer.writerow(
            [
                row.email,
                row.player_name,
                row.company_name,
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
