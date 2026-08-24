import pytest

from app.config_validation import validate_environment


def test_allows_missing_environment():
    """Local dev, where ENVIRONMENT usually isn't set at all."""
    validate_environment({})


def test_allows_development():
    validate_environment({"ENVIRONMENT": "development"})


def test_rejects_unrecognized_environment_value():
    # e.g. wrong casing — a typo, not a deliberate choice, so it
    # should fail loudly rather than silently behave like "not
    # production".
    with pytest.raises(RuntimeError):
        validate_environment({"ENVIRONMENT": "Production"})


def test_production_requires_admin_export_key():
    with pytest.raises(RuntimeError):
        validate_environment(
            {
                "ENVIRONMENT": "production",
                "FRONTEND_URL": "https://example.com",
            }
        )


def test_production_requires_frontend_url():
    with pytest.raises(RuntimeError):
        validate_environment(
            {
                "ENVIRONMENT": "production",
                "ADMIN_EXPORT_KEY": "a-very-secret-key",
            }
        )


def test_accepts_complete_production_config():
    validate_environment(
        {
            "ENVIRONMENT": "production",
            "ADMIN_EXPORT_KEY": "a-very-secret-key",
            "FRONTEND_URL": "https://example.com",
        }
    )
