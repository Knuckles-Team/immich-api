import importlib

import pytest


@pytest.mark.concept("IMMICH-001")
def test_package_imports():
    """Top-level package exposes its public API. CONCEPT:IMMICH-001"""
    module = importlib.import_module("immich_api")
    assert hasattr(module, "__all__")
