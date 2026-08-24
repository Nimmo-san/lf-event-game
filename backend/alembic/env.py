import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# So `import app...` below resolves regardless of the working
# directory `alembic` is invoked from (this file lives at
# backend/alembic/env.py, so parents[1] is backend/).
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Importing the model modules (not just app.database) registers every
# mapped class onto Base.metadata — target_metadata would otherwise be
# empty, since SQLAlchemy only knows about a model once its module has
# actually been imported somewhere.
import app.models.admin  # noqa: E402,F401
import app.models.game  # noqa: E402,F401
import app.models.leaderboard  # noqa: E402,F401
from app.database import Base, DATABASE_URL  # noqa: E402

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
#
# disable_existing_loggers=False: the default (True) silently disables
# every logger the app already created before this ran — fine when
# `alembic` is invoked as its own CLI process, but when it's driven
# programmatically from within the same process as the app (e.g. the
# migration test in tests/test_migrations.py), the default would
# disable app.routes.*'s loggers for the rest of that process.
if config.config_file_name is not None:
    fileConfig(config.config_file_name, disable_existing_loggers=False)

# Drive the DB URL from the same env-var logic app.database already
# uses (DATABASE_DIR, defaulting to backend/data locally / a Render
# persistent disk in production), rather than duplicating it in
# alembic.ini where it could drift out of sync. Only as a default,
# though — if a caller already set sqlalchemy.url on this Config
# object (e.g. a test pointing at a scratch DB), respect that instead.
if not config.get_main_option("sqlalchemy.url"):
    config.set_main_option("sqlalchemy.url", DATABASE_URL)

target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
