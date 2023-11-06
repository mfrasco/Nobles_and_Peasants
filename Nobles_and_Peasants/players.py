"""Functions related to the players table."""
from random import uniform

from flask_login import current_user

from Nobles_and_peasants.query import fetch_one
from Nobles_and_Peasants.starting_coin import get_starting_coin_for_status


def randomly_choose_player_status(players):
    """Randomly choose a player's status based on the status of other players.

    Args:
        players (List[sqlite3.Row]): Information on each player in the party
    """
    statuses = [row["player_status"] for row in players]
    num_players = len(statuses)
    num_nobles = statuses.count("noble")
    if num_nobles < 2:
        return "noble"
    elif (float(num_nobles) / num_players) < 0.2:
        if uniform(0, 1) < 0.75:
            return "noble"
        else:
            return "peasant"
    else:
        return "peasant"


def insert_new_player(db, user_id, player_status):
    """Add a new row to the database for a new player."""
    party_id = current_user.id
    starting_coin = get_starting_coin_for_status(db=db, player_stats=player_status)

    if player_status == "peasant":
        noble_id = None
        soldiers = 0
    elif player_status == "noble":
        noble_id = user_id
        soldiers = 1

    query = """
        insert into players (id, party_id, player_status, coin, noble_id, drinks, soldiers)
        values (?, ?, ?, ?, ?, ?, ?)
    """
    args = [user_id, party_id, player_status, starting_coin, noble_id, 0, soldiers]
    db.execute(query, args)
    db.commit()


def get_all_player_info(db):
    """Get information for all players in a party."""
    party_id = current_user.id
    query = """
        select id, player_status, coin, noble_id, drinks, soldiers
        from players
        where party_id = ?
        order by id
    """
    return db.execute(query, [party_id]).fetchall()


def get_all_nobles(db):
    """Get information for all nobles in a party."""
    party_id = current_user.id
    query = """
        select id, soldiers, coin, drinks
        from players
        where party_id = ?
            and player_status = 'noble'
        order by soldiers desc, coin desc, drinks desc
    """
    return db.execute(query, [party_id]).fetchall()


def get_almighty_ruler(db):
    """Find the noble with the most soldiers in their army."""
    party_id = current_user.id
    query = """
        select id
        from players
        where party_id = ?
        order by soldiers desc
        limit 1
    """
    return fetch_one(db, query, [party_id])


def get_single_player_info(db, user_id):
    """Get information for all players in a party."""
    party_id = current_user.id
    query = """
        select id, player_status, coin, noble_id, drinks, soldiers
        from players
        where party_id = ?
            and id = ?
    """
    return db.execute(query, [party_id, user_id]).fetchall()[0]


def find_richest_peasant(db):
    """Find the peasant id with the most coin."""
    party_id = current_user.id
    query = """
        select id
        from players
        where party_id = ?
            and player_status = 'peasant'
        order by coin desc, drinks desc
        limit 1
    """
    return fetch_one(db, query, [party_id])


def increment_soldiers_for_noble(db, user_id, num):
    """Change the number of soliders for a given user."""
    party_id = current_user.id
    query = """
    update players
    set soldiers = soldiers + ?
    where party_id = ?
        and id = ?
    """
    db.execute(query, [num, party_id, user_id])
    db.commit()


def set_allegiance_for_user(db, user_id, noble_id):
    """Update database with noble id for a given user."""
    party_id = current_user.id
    query = """
        update players
        set noble_id = ?
        where party_id = ?
            and id = ?
    """
    db.execute(query, [noble_id, party_id, user_id])
    db.commit()


def update_info_after_pledge_allegiance(db, user_id, noble_id):
    """Update database when a user pledges allegiance to a noble."""
    # decrement the soldier count for the previous noble
    player = get_single_player_info(db=db, user_id=user_id)
    previous_noble_id = player["noble_id"]
    if previous_noble_id is not None:
        increment_soldiers_for_noble(db=db, user_id=previous_noble_id, num=-1)

    set_allegiance_for_user(db=db, user_id=user_id, noble_id=noble_id)
    increment_soldiers_for_noble(db=db, user_id=noble_id, num=1)


def increment_coin_for_user(db, user_id, coin):
    """Increase the value of coin for a user."""
    party_id = current_user.id
    query = """
        update players
        set coin = coin + ?
        where party_id = ?
            and id = ?
    """
    db.execute(query, [coin, party_id, user_id])
    db.commit()


def move_coin_from_user_to_user(db, from_id, to_id):
    """Move coin from one user to another."""
    from_coin = get_single_player_info(db=db, user_id=from_id)["coin"]
    if from_coin > 0:
        increment_coin_for_user(db=db, user_id=from_id, coin=-from_coin)
        increment_coin_for_user(db=db, user_id=to_id, coin=from_coin)


def increment_soldiers_for_user(db, user_id, num):
    """Increase the number of soliders for a single user."""
    party_id = current_user.id
    query = """
        update players
        set soldiers = soldiers + ?
        where party_id = ?
            and id = ?
    """
    db.execute(query, [num, party_id, user_id])
    db.commit()


def increment_drinks_for_user(db, user_id, num):
    """Increase the number of drinks for a user."""
    party_id = current_user.id
    query = """
        update players
        set drinks = drinks + ?
        where party_id = ?
            and id = ?
    """
    db.execute(query, [num, party_id, user_id])
    db.commit()


def change_allegiances_between_nobles(db, old_noble_id, new_noble_id):
    """For every player, if they are allied to old_noble_id, make them allied to new_noble_id."""
    party_id = current_user.id
    query = """
        update players
        set noble_id = ?
        where party_id = ?
            and noble_id = ?
    """
    db.execute(query, [new_noble_id, party_id, old_noble_id])
    db.commit()


def change_peasant_to_noble(db, user_id):
    """Update info for a user to reflect their new status as a noble."""
    party_id = current_user.id
    starting_coin = get_starting_coin_for_status(db=db, player_stats="noble")
    query = """
        update players
        set player_status = "noble"
            , noble_id = ?
            , coin = max(?, coin + ?)
            , soldiers = 1 + (
                select count(*)
                from players
                where party_id = ?
                    and noble_id = ?
                    and id != ?
            )
        where party_id = ?
            and id = ?
    """
    args = [
        user_id,
        starting_coin,
        starting_coin,
        party_id,
        user_id,
        user_id,
        party_id,
        user_id,
    ]
    db.execute(query, args)
    db.commit()


def change_noble_to_peasant(db, user_id):
    """Update info for a user to reflect their new status as a peasant."""
    party_id = current_user.id
    query = """
        update players
        set player_status = 'peasant'
            , soldiers = 0
        where party_id = ?
            and id = ?
    """
    db.execute(query, [party_id, user_id])
    db.commit()


def upgrade_peasant_and_downgrade_noble(db, peasant_id, noble_id):
    """Turn a peasant into a noble. And turn a noble into a peasant."""
    move_coin_from_user_to_user(db=db, from_id=noble_id, to_id=peasant_id)

    peasant = get_single_player_info(db=db, user_id=peasant_id)

    # if the new noble is allied to another noble,
    # remove the new noble from that army
    if peasant["noble_id"] is not None:
        increment_soldiers_for_user(db=db, user_id=peasant["noble_id"], num=-1)

    change_allegiances_between_nobles(
        db=db, old_noble_id=noble_id, new_noble_id=peasant_id
    )
    change_peasant_to_noble(db=db, user_id=peasant_id)
    change_noble_to_peasant(db=db, user_id=noble_id)
