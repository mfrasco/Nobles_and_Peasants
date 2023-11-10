"""Database module."""
import sqlite3

import click
from flask import current_app, g


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect("instance/nobles_and_peasants.sqlite")
    rv.row_factory = sqlite3.Row
    return rv


def get_db():
    """Get database connection."""
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    """Close database connection."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Initialize database."""
    db = get_db()
    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))


@click.command("init-db")
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")


def init_app(app):
    """Initialize the app."""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
