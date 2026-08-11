import os
from pathlib import Path

from sqlalchemy import create_engine
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


engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
)


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
