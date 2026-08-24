from fastapi import Depends
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from sqlalchemy import text
from sqlalchemy.orm import Session

import os
from dotenv import load_dotenv

from app.models.admin import AdminSession

from app.database import Base
from app.database import engine
from app.database import get_db
from app.rate_limit import limiter

from app.routes.players import router as player_router
from app.routes.leaderboard import (
    router as leaderboard_router,
)
from app.routes.admin import router as admin_router


load_dotenv()

Base.metadata.create_all(
    bind=engine,
)

app = FastAPI(
    title="Lightning Flight API",
    version="1.0.0",
)

app.state.limiter = limiter

app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)

# Local dev origins are always allowed. The production
# frontend origin comes from an env var (set in Render's
# dashboard, not committed to code) so the URL can change
# without needing a code edit + redeploy.
allowed_origins = [
    "http://localhost:5173",
    "http://localhost:4173",
]

frontend_url = os.environ.get("FRONTEND_URL")

if frontend_url:
    allowed_origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    player_router,
)

app.include_router(
    leaderboard_router,
)

app.include_router(
    admin_router,
)


@app.get("/health")
def health(db: Session = Depends(get_db)):
    # A trivial query, not just "is the process up" — the previous
    # version returned 200 unconditionally, so a Render disk issue
    # (unmounted/full persistent disk under the SQLite file) would
    # still show green while every real request 500s.
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "error",
                "service": "lightning-flight-api",
                "detail": "Database unreachable.",
            },
        )

    return {
        "status": "ok",
        "service": "lightning-flight-api",
    }
