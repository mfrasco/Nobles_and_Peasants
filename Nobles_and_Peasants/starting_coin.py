"""Functions related to the starting_coin table."""
from flask_login import current_user

from nobles_and_peasants.query import fetch_one


def get_status_and_starting_coin(db):
    """Get the starting coin for each player status."""
    party_id = current_user.id
    query = """
        select player_status, coin
        from starting_coin
        where party_id = ?
        order by coin
    """
    return db.execute(query, [party_id]).fetchall()


def get_starting_coin_for_status(db, player_status):
    """Get the starting coin for a single player status."""
    party_id = current_user.id
    query = """
        select coin
        from starting_coin
        where party_id = ?
            and player_status = ?
    """
    return fetch_one(db, query, [party_id, player_status])


def update_noble_starting_coin(db, noble_coin):
    """Update the starting coin that a noble receives."""
    party_id = current_user.id
    query = """
        update starting_coin
        set coin = ?
        where party_id = ?
            and player_status = 'noble'
    """
    db.execute(query, [noble_coin, party_id])
    db.commit()
