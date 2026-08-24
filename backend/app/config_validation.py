"""Fail-fast checks for required production configuration.

Called once at app.main import time. Kept as a plain function taking an
explicit environment mapping (rather than reading os.environ directly)
so it can be unit tested against a synthetic environment without
needing to re-trigger app.main's module-level import side effects.

Without this, a misconfigured ENVIRONMENT value degrades silently
instead of failing loudly:

- routes/admin.py's IS_PRODUCTION only becomes True when ENVIRONMENT
  is exactly "production". Anything else (a typo, wrong casing, or
  simply forgetting to set it) drops the Secure flag from the admin
  session cookie, which is always SameSite=None — browsers discard
  that cookie outright, breaking admin login with no server-side
  error pointing at the cause.
- routes/admin.py's ADMIN_EXPORT_KEY, if unset, makes admin_key_matches()
  always return False — admin login always 401s, again with nothing
  in the logs explaining why.
- main.py's CORS allow-list only includes the deployed frontend's
  origin if FRONTEND_URL is set — without it, every API call from the
  production frontend fails as a CORS error.
"""

# from typing import Mapping
from collections.abc import Mapping

REQUIRED_IN_PRODUCTION = ("ADMIN_EXPORT_KEY", "FRONTEND_URL")
VALID_ENVIRONMENTS = {"production", "development"}


def validate_environment(env: Mapping[str, str]) -> None:
    environment = env.get("ENVIRONMENT")

    # Unset is fine (local dev). Anything set but not recognized is
    # almost certainly a typo, and — unlike unset — it's not a state
    # anyone would choose on purpose, so it's worth failing loudly.
    if environment is not None and environment not in VALID_ENVIRONMENTS:
        raise RuntimeError(
            f"ENVIRONMENT={environment!r} is not one of "
            f"{sorted(VALID_ENVIRONMENTS)}. If this is a production "
            "deploy, set ENVIRONMENT=production exactly — anything else "
            "silently disables the Secure flag on the admin session "
            "cookie, which browsers then discard outright."
        )

    if environment != "production":
        return

    missing = [name for name in REQUIRED_IN_PRODUCTION if not env.get(name)]

    if missing:
        raise RuntimeError(
            "Missing required production environment variable(s): "
            f"{', '.join(missing)}."
        )
