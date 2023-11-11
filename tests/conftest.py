"""Configure tests."""
import os
import tempfile

import pytest
from nobles_and_peasants import create_app
from nobles_and_peasants.db import get_db, init_db

with open(os.path.join(os.path.dirname(__file__), "test_data.sql"), "rb") as f:
    _data_sql = f.read().decode("utf8")


@pytest.fixture
def app():
    """Create an app object that can be used to test functionality."""
    db_fd, db_path = tempfile.mkstemp()

    app = create_app(
        {
            "TESTING": True,
            "DATABASE": db_path,
        }
    )

    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Create a client to make requests to the app without running a server."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a runner to execute the click commands."""
    return app.test_cli_runner()


class AuthActions:
    """Simplify authentication actions."""

    def __init__(self, client):
        """Initialize authentication client."""
        self._client = client

    def login(self, party_name, password):
        """Log in to a party."""
        return self._client.post(
            "/auth/login",
            data={"party_name": party_name, "password": password},
            follow_redirects=True,

        )

    def logout(self):
        """Log out of a party."""
        return self._client.get("/auth/logout", follow_redirects=True)


@pytest.fixture
def auth(client):
    """A fixture for logging in and logging out."""
    return AuthActions(client)
