from sqlalchemy import text

from app.database import engine


def test_wal_mode_is_enabled():
    with engine.connect() as connection:
        journal_mode = connection.execute(text("PRAGMA journal_mode")).scalar()

    assert journal_mode == "wal"


def test_busy_timeout_is_configured():
    with engine.connect() as connection:
        # SQLite reports this in milliseconds regardless of how it
        # was set; connect_args passes seconds to sqlite3.connect().
        busy_timeout_ms = connection.execute(text("PRAGMA busy_timeout")).scalar()

    assert busy_timeout_ms == 5_000
