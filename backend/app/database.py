import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy import event
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import sessionmaker


BASE_DIR = Path(__file__).resolve().parent.parent

# Local dev: defaults to backend/data.
#
# Production: set DATABASE_DIR to an absolute path on a
# Render persistent disk (e.g. /var/data) via an env var.
# This decouples the DB's location from wherever the repo
# happens to be checked out on disk.
DATABASE_DIR = Path(
    os.environ.get("DATABASE_DIR", str(BASE_DIR / "data")),
)

DATABASE_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

DATABASE_URL = f"sqlite:///{DATABASE_DIR / 'lightning_quest.db'}"

# How long a connection waits for a lock before raising "database is
# locked", rather than failing immediately. SQLAlchemy forwards this
# straight to sqlite3.connect(), where it already defaults to 5.0s —
# set explicitly here so the intended value is visible rather than
# relying on that default.
SQLITE_LOCK_TIMEOUT_SECONDS = 5.0


engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,
        "timeout": SQLITE_LOCK_TIMEOUT_SECONDS,
    },
)


@event.listens_for(engine, "connect")
def _enable_wal_mode(dbapi_connection, connection_record):
    # SQLite's default rollback-journal mode blocks every reader for
    # the duration of a writer's transaction (and vice versa) — at a
    # live event, a burst of GET /api/leaderboard requests landing
    # alongside a POST /api/games is exactly the kind of thing that
    # turns into "database is locked" errors. WAL mode lets readers
    # proceed concurrently with a single writer instead. There's no
    # connect_args equivalent for this — it has to be set via PRAGMA
    # on every new connection.
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.close()


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()
