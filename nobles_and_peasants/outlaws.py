"""Functions related to the outlaws table."""
from flask import session

from nobles_and_peasants.db import execute, fetch_all


def is_peasant_banned(noble_id, peasant_id):
    """Check if a peasant is banned from a noble's army."""
    party_id = session.get("party_id")
    query = """
        select peasant_id
        from outlaws
        where party_id = ?
            and noble_id = ?
    """
    outlaws = fetch_all(query=query, args=[party_id, noble_id])
    banned_peasants = [x["peasant_id"] for x in outlaws]
    return peasant_id in banned_peasants


def insert_new_outlaw(noble_id, peasant_id, commit):
    """Add a new row to the database for a noble to ban a peasant."""
    party_id = session.get("party_id")
    query = """
        insert into outlaws (party_id, noble_id, peasant_id) values (?, ?, ?)
    """
    execute(query=query, args=[party_id, noble_id, peasant_id], commit=commit)
