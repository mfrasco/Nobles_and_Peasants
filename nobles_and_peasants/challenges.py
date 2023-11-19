"""Functions related to the challenges table."""
from flask import session

from nobles_and_peasants.query import execute, fetch_all, fetch_one


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


def get_all_challenges():
    """Get all challenges in a given party."""
    party_id = session.get("party_id")
    query = """
        select id, challenge
        from challenges
        where party_id = ?
        order by id
    """
    return fetch_all(query=query, args=[party_id])


def is_challenge_in_party(challenge_id):
    """Check if a challenge_id is associated with a given party."""
    challenges = [c["id"] for c in get_all_challenges()]
    return challenge_id in challenges


def add_challenge_to_party(challenge, commit=True):
    """Add a row to the database for a new challenge."""
    party_id = session.get("party_id")
    query = """
        insert into challenges (party_id, challenge) values (?, ?)
    """
    execute(query=query, args=[party_id, challenge], commit=commit)


def delete_challenge_from_table(challenge_id, commit=True):
    """Delete a row from the database for a challenge."""
    query = """
        delete from challenges where id = ?
    """
    execute(query=query, args=[challenge_id], commit=commit)
