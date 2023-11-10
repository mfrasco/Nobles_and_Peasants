"""Functions related to the players table."""
from random import uniform

from flask import session

from nobles_and_peasants.constants import NOBLE, PEASANT
from nobles_and_peasants.query import fetch_one
from nobles_and_peasants.starting_coin import get_starting_coin_for_status


def randomly_choose_player_status(players):
    """Randomly choose a player's status based on the status of other players.

    Args:
        players (List[sqlite3.Row]): Information on each player in the party
    """
    statuses = [row["player_status"] for row in players]
    num_players = len(statuses)
    num_nobles = statuses.count(NOBLE)
    if num_nobles < 2:
        return NOBLE
    elif (float(num_nobles) / num_players) < 0.2:
        if uniform(0, 1) < 0.75:
            return NOBLE
        else:
            return PEASANT
    else:
        return PEASANT


def insert_new_player(db, player_name, player_status):
    """Add a new row to the database for a new player."""
    party_id = session.get("party_id")
    starting_coin = get_starting_coin_for_status(db=db, player_status=player_status)

    if player_status == PEASANT:
        noble_name = None
        soldiers = 0
    elif player_status == NOBLE:
        noble_name = player_name
        soldiers = 1

    query = """
        insert into players (party_id, player_name, player_status, coin, noble_name, drinks, soldiers)
        values (?, ?, ?, ?, ?, ?, ?)
    """
    args = [
        party_id,
        player_name,
        player_status,
        starting_coin,
        noble_name,
        0,
        soldiers,
    ]
    db.execute(query, args)
    db.commit()


def get_all_players(db):
    """Get information for all players in a party."""
    party_id = session.get("party_id")
    query = """
        select
            id
            , player_name
            , player_status
            , coin
            , noble_name
            , drinks
            , soldiers
        from players
        where party_id = ?
        order by player_name
    """
    return db.execute(query, [party_id]).fetchall()


def get_all_nobles(db):
    """Get information for all nobles in a party."""
    party_id = session.get("party_id")
    query = """
        select id, player_name, soldiers, coin, drinks
        from players
        where party_id = ?
            and player_status = 'noble'
        order by soldiers desc, coin desc, drinks desc
    """
    return db.execute(query, [party_id]).fetchall()


def get_almighty_ruler(db):
    """Find the noble with the most soldiers in their army."""
    party_id = session.get("party_id")
    query = """
        select player_name
        from players
        where party_id = ?
        order by soldiers desc
        limit 1
    """
    return fetch_one(db, query, [party_id])


def get_single_player(db, player_name, col=None):
    """Get information for all players in a party."""
    party_id = session.get("party_id")
    if col is None:
        query = """
            select id, player_status, coin, noble_name, drinks, soldiers
            from players
            where party_id = ?
                and player_name = ?
        """
        return db.execute(query, [party_id, player_name]).fetchall()[0]
    else:
        query = f"""
            select {col}
            from players
            where party_id = ?
                and player_name = ?
        """
        return fetch_one(db, query, [party_id, player_name])


def find_richest_peasant(db):
    """Find the peasant name with the most coin."""
    party_id = session.get("party_id")
    query = """
        select player_name
        from players
        where party_id = ?
            and player_status = 'peasant'
        order by coin desc, drinks desc
        limit 1
    """
    return fetch_one(db, query, [party_id])


def set_allegiance(db, player_name, noble_name):
    """Update database with noble id for a given player."""
    party_id = session.get("party_id")
    query = """
        update players
        set noble_name = ?
        where party_id = ?
            and player_name = ?
    """
    db.execute(query, [noble_name, party_id, player_name])
    db.commit()


def update_after_pledge_allegiance(db, player_name, noble_name):
    """Update database when a player pledges allegiance to a noble."""
    # decrement the soldier count for the previous noble
    player = get_single_player(db=db, player_name=player_name)
    previous_noble_name = player["noble_name"]
    if previous_noble_name is not None:
        increment_soldiers(db=db, player_name=previous_noble_name, num=-1)

    set_allegiance(db=db, player_name=player_name, noble_name=noble_name)
    increment_soldiers(db=db, player_name=noble_name, num=1)


def increment_coin(db, player_name, coin):
    """Increase the amount of coin for a player."""
    party_id = session.get("party_id")
    query = """
        update players
        set coin = coin + ?
        where party_id = ?
            and player_name = ?
    """
    db.execute(query, [coin, party_id, player_name])
    db.commit()


def move_coin_between_players(db, from_name, to_name):
    """Move coin from one player to another."""
    from_coin = get_single_player(db=db, player_name=from_name, col="coin")
    if from_coin > 0:
        increment_coin(db=db, player_name=from_name, coin=-from_coin)
        increment_coin(db=db, player_name=to_name, coin=from_coin)


def increment_soldiers(db, player_name, num):
    """Increase the number of soliders for a single player."""
    party_id = session.get("party_id")
    query = """
        update players
        set soldiers = soldiers + ?
        where party_id = ?
            and player_name = ?
    """
    db.execute(query, [num, party_id, player_name])
    db.commit()


def increment_drinks(db, player_name, num):
    """Increase the number of drinks for a player."""
    party_id = session.get("party_id")
    query = """
        update players
        set drinks = drinks + ?
        where party_id = ?
            and player_name = ?
    """
    db.execute(query, [num, party_id, player_name])
    db.commit()


def change_allegiances_between_nobles(db, old_noble_name, new_noble_name):
    """For every player, if they are allied to old_noble_name, make them allied to new_noble_name."""
    party_id = session.get("party_id")
    query = """
        update players
        set noble_name = ?
        where party_id = ?
            and noble_name = ?
    """
    db.execute(query, [new_noble_name, party_id, old_noble_name])
    db.commit()


def change_peasant_to_noble(db, player_name):
    """Update info for a player to reflect their new status as a noble."""
    party_id = session.get("party_id")
    starting_coin = get_starting_coin_for_status(db=db, player_status=NOBLE)
    query = """
        update players
        set player_status = 'noble'
            , noble_name = ?
            , coin = max(?, coin + ?)
            , soldiers = 1 + (
                select count(*)
                from players
                where party_id = ?
                    and noble_name = ?
                    and player_name != ?
            )
        where party_id = ?
            and player_name = ?
    """
    args = [
        player_name,
        starting_coin,
        starting_coin,
        party_id,
        player_name,
        player_name,
        party_id,
        player_name,
    ]
    db.execute(query, args)
    db.commit()


def change_noble_to_peasant(db, player_name):
    """Update info for a player to reflect their new status as a peasant."""
    party_id = session.get("party_id")
    query = """
        update players
        set player_status = 'peasant'
            , soldiers = 0
        where party_id = ?
            and player_name = ?
    """
    db.execute(query, [party_id, player_name])
    db.commit()


def upgrade_peasant_and_downgrade_noble(db, peasant_name, noble_name):
    """Turn a peasant into a noble. And turn a noble into a peasant."""
    move_coin_between_players(db=db, from_name=noble_name, to_name=peasant_name)

    peasant = get_single_player(db=db, player_name=peasant_name)

    # if the new noble is allied to another noble,
    # remove the new noble from that army
    if peasant["noble_name"] is not None:
        increment_soldiers(db=db, player_name=peasant["noble_name"], num=-1)

    change_allegiances_between_nobles(
        db=db, old_noble_name=noble_name, new_noble_name=peasant_name
    )
    change_peasant_to_noble(db=db, player_name=peasant_name)
    change_noble_to_peasant(db=db, player_name=noble_name)
