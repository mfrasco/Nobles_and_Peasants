"""Functions related to the starting_coin table."""
from flask import session

from nobles_and_peasants.query import execute, fetch_one, fetch_all


def get_status_and_starting_coin():
    """Get the starting coin for each player status."""
    party_id = session.get("party_id")
    query = """
        select player_status, coin
        from starting_coin
        where party_id = ?
        order by coin
    """
    return fetch_all(query=query, args=[party_id])


def get_starting_coin_for_status(player_status):
    """Get the starting coin for a single player status."""
    party_id = session.get("party_id")
    query = """
        select coin
        from starting_coin
        where party_id = ?
            and player_status = ?
    """
    return fetch_one(query=query, args=[party_id, player_status])


def update_noble_starting_coin(noble_coin):
    """Update the starting coin that a noble receives."""
    party_id = session.get("party_id")
    query = """
        update starting_coin
        set coin = ?
        where party_id = ?
            and player_status = 'noble'
    """
    execute(query=query, args=[noble_coin, party_id], commit=True)
