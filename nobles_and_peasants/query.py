"""Helper functions for executing queries."""

from nobles_and_peasants.db import get_db


def fetch_one(query, args):
    """Execute a query where we are intending to get a single value."""
    cur = get_db().execute(query, args)
    result = cur.fetchone()
    cur.close()
    if result is None:
        return None
    else:
        return result[0]


def fetch_all(query, args):
    """Execute a query where we are intending to get multiple values."""
    cur = get_db().execute(query, args)
    result = cur.fetchall()
    cur.close()
    return result


def execute(query, args, commit):
    """Execute a query where we are intending to write results to the database."""
    db = get_db()
    db.execute(query, args)
    if commit:
        db.commit()
