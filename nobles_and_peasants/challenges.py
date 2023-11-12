"""Functions related to the challenges table."""
from flask import session

from nobles_and_peasants.query import fetch_one


def get_random_challenge():
    """Get a random challenge."""
    party_id = session.get("party_id")
    query = """
        select challenge
        from challenges
        where party_id = ?
        order by random()
        limit 1
    """
    return fetch_one(query=query, args=[party_id])
