"""Tests for app factory."""
from nobles_and_peasants import create_app


def test_config():
    """Test that testing mode is set properly when an app is created."""
    assert not create_app().testing
    assert create_app({"TESTING": True}).testing
