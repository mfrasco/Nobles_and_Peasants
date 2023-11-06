from flask_login import current_user

from Nobles_and_peasants.query import fetch_one


def get_random_quest(db, difficulty):
    """Get a random quest of a certain difficulty."""
    party_id = current_user.id
    query = """
        select quest
        from quests
        where party_id = ?
            and difficulty = ?
        order by random()
        limit 1
    """
    return fetch_one(db, query, [party_id, difficulty])
