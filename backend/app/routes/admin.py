import csv
import io
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

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.admin import AdminSession
from app.database import get_db
from app.models.game import GameResult
from app.models.leaderboard import LeaderboardEntry
from app.rate_limit import limiter
from app.schemas.player import MarketingExportRequest


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

    token_hash = hash_sesion_token(
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


def hash_sesion_token(
    token: str,
) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


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
        raise HTTPException(
            status_code=401,
            detail="Invalid admin key.",
        )

    # token generation
    raw_token = secrets.token_urlsafe(32)

    token_hash = hash_sesion_token(raw_token)

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
        token_hash = hash_sesion_token(
            raw_token,
        )

        session = (
            db.query(AdminSession).filter(AdminSession.token_hash == token_hash).first()
        )

        if session:
            db.delete(session)
            db.commit()

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
    _: AdminSession = Depends(require_admin),
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


@router.post("/export/marketing")
@limiter.limit("10/minute")
def export_marketing_data(
    request: Request,
    payload: MarketingExportRequest,
    db: Session = Depends(get_db),
    _: AdminSession = Depends(require_admin),
):
    query = db.query(
        LeaderboardEntry.id,
        LeaderboardEntry.email,
        LeaderboardEntry.created_at,
        GameResult.player_name,
        GameResult.company_name,
    ).join(
        GameResult,
        GameResult.id == LeaderboardEntry.game_id,
    )

    if payload.search:
        value = f"%{payload.search.strip()}%"

        query = query.filter(
            or_(
                GameResult.player_name.ilike(value),
                GameResult.company_name.ilike(value),
                LeaderboardEntry.email.ilike(value),
            )
        )

    if payload.name:
        query = query.filter(GameResult.player_name.ilike(f"%{payload.name.strip()}%"))

    if payload.email:
        query = query.filter(LeaderboardEntry.email.ilike(f"%{payload.email.strip()}%"))

    if payload.company:
        query = query.filter(
            GameResult.company_name.ilike(f"%{payload.company.strip()}%")
        )

    if payload.excluded_ids:
        query = query.filter(
            ~LeaderboardEntry.id.in_(
                payload.excluded_ids,
            )
        )

    rows = query.order_by(
        LeaderboardEntry.created_at.asc(),
    ).all()

    output = io.StringIO()

    writer = csv.writer(output)

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
