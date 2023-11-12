"""Functions related to the quest_rewards table."""
from flask import session

from nobles_and_peasants.query import fetch_one, fetch_all


def get_quest_difficulty_and_reward():
    """Get the reward for each quest difficulty."""
    party_id = session.get("party_id")
    query = """
        select difficulty, reward
        from quest_rewards
        where party_id = ?
        order by reward
    """
    return fetch_all(query=query, args=[party_id])


def get_reward_for_difficulty(difficulty):
    """Get the quest reward for a given difficulty."""
    party_id = session.get("party_id")
    query = """
        select reward
        from quest_rewards
        where party_id = ?
            and difficulty = ?
    """
    return fetch_one(query=query, args=[party_id, difficulty])


def set_quest_rewards(easy_reward, medium_reward, hard_reward):
    """Set the quest rewards for each difficulty."""
    party_id = session.get("party_id")
    query = """
        update quest_rewards
        set reward = (case when difficulty = 'easy' then ?
                        when difficulty = 'medium' then ?
                        else ?
                    end)
        where party_id = ?
    """
    args = [easy_reward, medium_reward, hard_reward, party_id]
    execute(query=query, args=args, commit=True)
