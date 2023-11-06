"""Functions related to the quest_rewards table."""
from flask_login import current_user

from Nobles_and_Peasants.query import fetch_one


def get_quest_difficulty_and_reward(db):
    """Get the reward for each quest difficulty."""
    party_id = current_user.id
    query = """
        select difficulty, reward
        from quest_rewards
        where party_id = ?
        order by reward
    """
    return db.execute(query, [party_id]).fetchall()


def get_reward_for_difficulty(db, difficulty):
    """Get the quest reward for a given difficulty."""
    party_id = current_user.id
    query = """
        select reward
        from quest_rewards
        where party_id = ?
            and difficulty = ?
    """
    return fetch_one(db, query, [party_id, difficulty])


def set_quest_rewards(db, easy_reward, medium_reward, hard_reward):
    """Set the quest rewards for each difficulty."""
    party_id = current_user.id
    query = """
        update quest_rewards
        set reward = (case when difficulty = 'easy' then ?
                        when difficulty = 'medium' then ?
                        else ?
                    end)
        where party_id = ?
    """
    args = [easy_reward, medium_reward, hard_reward, party_id]
    db.execute(query, args)
    db.commit()
