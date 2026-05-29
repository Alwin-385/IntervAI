"""Tests for application configuration and environment handling."""

import pytest

pytestmark = pytest.mark.unit


def test_settings_loads_without_error(settings):
    assert settings is not None
    assert settings.app_name


def test_default_environment_is_development(settings):
    assert settings.environment == "development"


def test_is_development_flag(settings):
    assert settings.is_development is True
    assert settings.is_production is False


def test_cors_origins_list_parsed(settings):
    origins = settings.cors_origins_list
    assert isinstance(origins, list)
    assert len(origins) >= 1
    for origin in origins:
        assert origin.startswith("http")


def test_database_url_has_asyncpg_scheme(settings):
    assert "asyncpg" in str(settings.database_url)


def test_rate_limit_defaults(settings):
    assert settings.rate_limit_default_rpm > 0
    assert settings.rate_limit_ai_rpm > 0
    assert settings.rate_limit_upload_rpm > 0


def test_sentry_dsn_none_by_default(settings):
    # In test env we set SENTRY_DSN=""
    assert not settings.sentry_dsn
