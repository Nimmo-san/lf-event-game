import atexit
import os
import shutil
import tempfile

# Must happen before `app.database`/`app.routes.admin` are imported
# anywhere (they read these at import time), so the test suite never
# touches the real dev database under backend/data/, and admin-route
# tests have a known key to log in with — without this,
# ADMIN_EXPORT_KEY is unset and admin login always 401s regardless of
# what's submitted.
_TEST_DB_DIR = tempfile.mkdtemp(prefix="lightning-flight-test-")
os.environ["DATABASE_DIR"] = _TEST_DB_DIR
atexit.register(shutil.rmtree, _TEST_DB_DIR, ignore_errors=True)

TEST_ADMIN_EXPORT_KEY = "test-admin-export-key"
os.environ.setdefault("ADMIN_EXPORT_KEY", TEST_ADMIN_EXPORT_KEY)

import pytest
from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app
from app.rate_limit import limiter


@pytest.fixture(autouse=True)
def _reset_state():
    """Fresh tables and a clean rate-limit bucket for every test.

    The app/limiter are module-level singletons shared across the whole
    test session, so without this, tests would see each other's rows and
    could trip a route's per-minute limit purely from earlier tests.
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    limiter.reset()

    yield


@pytest.fixture()
def client():
    with TestClient(app) as test_client:
        yield test_client
