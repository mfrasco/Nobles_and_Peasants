"""Functions related to the quests table."""
from flask import session

from nobles_and_peasants.query import execute, fetch_all, fetch_one


def get_random_quest(difficulty):
    """Get a random quest of a certain difficulty."""
    party_id = session.get("party_id")
    query = """
        select quest
        from quests
        where party_id = ?
            and difficulty = ?
        order by random()
        limit 1
    """
    return fetch_one(query=query, args=[party_id, difficulty])


def get_all_quests():
    """Get all quests in a given party."""
    party_id = session.get("party_id")
    query = """
        select id, quest, difficulty
        from quests
        where party_id = ?
        order by id
    """
    return fetch_all(query=query, args=[party_id])


def is_quest_in_party(quest_id):
    """Check if a quest_id is associated with a given party."""
    quests = [q["id"] for q in get_all_quests()]
    return quest_id in quests


def add_quest_to_party(quest, difficulty, commit=True):
    """Add a row to the database for a new quest."""
    party_id = session.get("party_id")
    query = """
        insert into quests (party_id, quest, difficulty) values (?, ?, ?)
    """
    execute(query=query, args=[party_id, quest, difficulty], commit=commit)


def delete_quest_from_table(quest_id, commit=True):
    """Delete a row from the database for a quest."""
    party_id = session.get("party_id")
    query = """
        delete from quests where id = ?
    """
    execute(query=query, args=[quest_id], commit=commit)