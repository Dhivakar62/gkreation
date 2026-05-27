"""
conftest.py — pytest fixtures and Django settings overrides for testing.
Disables SECURE_SSL_REDIRECT so test client works without HTTPS.
"""
import django
from django.test.utils import override_settings


def pytest_configure(config):
    """Override settings that cause 301 redirects in test environment."""
    from django.conf import settings
    # We do this via pytest-django's django_db_setup or settings override
    pass


# Apply SSL redirect override to all tests
import pytest

@pytest.fixture(autouse=True)
def disable_ssl_redirect(settings):
    """Disable SECURE_SSL_REDIRECT globally for all tests."""
    settings.SECURE_SSL_REDIRECT = False
    settings.SESSION_COOKIE_SECURE = False
    settings.CSRF_COOKIE_SECURE = False
