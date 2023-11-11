"""Functions related to the outlaws table."""
from flask import session


def is_peasant_banned(db, noble_id, peasant_id):
    """Check if a peasant is banned from a noble's army."""
    party_id = session.get("party_id")
    query = """
        select peasant_id
        from outlaws
        where party_id = ?
            and noble_id = ?
    """
    outlaws = db.execute(query, [party_id, noble_id]).fetchall()
    banned_peasants = [x["peasant_id"] for x in outlaws]
    return peasant_id in banned_peasants


def insert_new_outlaw(db, noble_id, peasant_id):
    """Add a new row to the database for a noble to ban a peasant."""
    party_id = session.get("party_id")
    query = """
        insert into outlaws (party_id, noble_id, peasant_id) values (?, ?, ?)
    """
    db.execute(query, [party_id, noble_id, peasant_id])
    db.commit()
