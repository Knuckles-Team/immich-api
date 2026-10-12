import pytest


@pytest.fixture(autouse=True)
def declared_auth_scheme(monkeypatch):
    """Canonical auth tests exercise bearer mode; provider cases override it."""
    monkeypatch.setenv("IMMICH_API_AUTH_SCHEME", "bearer")
