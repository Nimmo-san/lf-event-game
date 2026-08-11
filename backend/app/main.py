from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

import os
from dotenv import load_dotenv

from app.database import Base
from app.database import engine
from app.rate_limit import limiter

from app.routes.players import router as player_router
from app.routes.leaderboard import (
    router as leaderboard_router,
)


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


@app.get("/health")
def health():

    return {
        "status": "ok",
        "service": "lightning-flight-api",
    }