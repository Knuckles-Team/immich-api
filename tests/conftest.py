from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_api_client():
    client = MagicMock()
    client.get_system_status.return_value = {"status": "OK"}
    return client


@pytest.fixture(autouse=True)
def declared_auth_scheme(monkeypatch):
    """Canonical auth tests exercise the declared bearer mode; provider tests override it."""
    monkeypatch.setenv("IMMICH_API_AUTH_SCHEME", "bearer")
