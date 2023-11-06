"""Helper functions for executing queries."""

def fetch_one(db, query_string, args):
    """Execute a query where we are intending to get a single value."""
    rv = db.execute(query_string, args).fetchone()
    if rv is None:
        return None
    else:
        return rv[0]