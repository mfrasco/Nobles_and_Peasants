"""Functions related to the challenges table."""
from flask_login import current_user

from Nobles_and_peasants.query import fetch_one


def get_random_challenge(db):
    """Get a random challenge."""
    party_id = current_user.id
    query = """
        select challenge
        from challenges
        where party_id = ?
        order by random()
        limit 1
    """
    return fetch_one(db, query, [party_id])
