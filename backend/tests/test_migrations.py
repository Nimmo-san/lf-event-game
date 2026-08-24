from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect

import app.models.admin  # noqa: F401
import app.models.game  # noqa: F401
import app.models.leaderboard  # noqa: F401
from app.database import Base

BACKEND_DIR = Path(__file__).resolve().parent.parent


def _table_columns(engine) -> dict[str, list[str]]:
    inspector = inspect(engine)

    return {
        table: sorted(column["name"] for column in inspector.get_columns(table))
        for table in inspector.get_table_names()
        if table != "alembic_version"
    }


def test_alembic_upgrade_head_matches_current_models(tmp_path):
    """Applying every committed migration to a blank database must
    produce the exact schema the current models describe.

    This is what would catch a model changed without a matching
    migration being generated — the two are otherwise easy to let
    drift apart silently, which is exactly what happened once already
    before Alembic existed here (see the commented-out columns in
    models/game.py and models/leaderboard.py).
    """
    migrated_db = tmp_path / "migrated.db"

    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    config.set_main_option("sqlalchemy.url", f"sqlite:///{migrated_db}")

    command.upgrade(config, "head")

    migrated_engine = create_engine(f"sqlite:///{migrated_db}")

    current_models_db = tmp_path / "current_models.db"
    current_models_engine = create_engine(f"sqlite:///{current_models_db}")
    Base.metadata.create_all(bind=current_models_engine)

    assert _table_columns(migrated_engine) == _table_columns(current_models_engine)
