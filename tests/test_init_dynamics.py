import importlib

import pytest


@pytest.mark.concept("TEMPLATECONNECTOR-001")
def test_package_imports():
    """Top-level package exposes its public API. CONCEPT:TEMPLATECONNECTOR-001"""
    module = importlib.import_module("templateconnector_api")
    assert hasattr(module, "__all__")
