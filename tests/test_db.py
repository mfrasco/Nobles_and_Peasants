"""Tests for database connection."""
import sqlite3

import pytest
from nobles_and_peasants.db import get_db


def test_get_close_db(app):
    """Test that database connection closes outside of app context."""
    with app.app_context():
        db = get_db()
        assert db is get_db()

        query = "select count(*) as num from parties"
        num_parties = db.execute(query).fetchone()["num"]
        assert num_parties == 2

    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute("SELECT 1")

    assert "Cannot operate on a closed database" in str(e.value)


def test_init_db_command(runner, monkeypatch):
    """Test that initialize database command works."""

    class Recorder:
        called = False

    def fake_init_db():
        Recorder.called = True

    monkeypatch.setattr("nobles_and_peasants.db.init_db", fake_init_db)
    result = runner.invoke(args=["init-db"])
    assert "Initialized" in result.output
    assert Recorder.called
