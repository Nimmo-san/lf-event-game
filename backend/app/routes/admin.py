import csv
import io
import os
import secrets

from fastapi import (
    Request,
    APIRouter,
    Depends,
    Header,
    HTTPException,
)

from fastapi.responses import StreamingResponse

from sqlalchemy.orm import Session

from app.rate_limit import limiter
from app.database import get_db
from app.models.game import GameResult
from app.models.leaderboard import LeaderboardEntry


router = APIRouter(
    prefix="/api/admin",
    tags=["Admin"],
)


ADMIN_EXPORT_KEY = os.environ.get(
    "ADMIN_EXPORT_KEY",
)


def verify_admin_key(
    x_admin_key: str = Header(...),
):
    if (
        not ADMIN_EXPORT_KEY
        or not secrets.compare_digest(
            x_admin_key,
            ADMIN_EXPORT_KEY,
        )
    ):
        raise HTTPException(
            status_code=403,
            detail="Forbidden.",
        )


@router.get("/export/marketing")
@limiter.limit("10/minute")
def export_marketing_data(
    request: Request,
    db: Session = Depends(get_db),
    _: None = Depends(verify_admin_key),
):
    rows = (
        db.query(
            LeaderboardEntry.email,
            LeaderboardEntry.created_at,
            GameResult.player_name,
            GameResult.company_name,
        )
        .join(
            GameResult,
            GameResult.id == LeaderboardEntry.game_id,
        )
        .order_by(
            LeaderboardEntry.created_at.asc(),
        )
        .all()
    )

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
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": 'attachment; filename="lightning-flight-marketing.csv"'
        },
    )
