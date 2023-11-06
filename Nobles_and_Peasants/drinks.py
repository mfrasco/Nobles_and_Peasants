from flask_login import current_user

from Nobles_and_peasants.query import fetch_one


def get_drink_name_and_cost(db):
    """Get all drink names and costs."""
    party_id = current_user.id
    query = """
        select drink_name, drink_cost
        from drinks
        where party_id = ?
        order by drink_cost
    """
    return db.execute(query, [party_id]).fetchall()


def get_cost_for_a_drink(db, drink_name):
    """Get the cost for a single drink."""
    party_id = current_user.id
    query = """
        select drink_cost
        from drinks
        where party_id = ?
            and drink_name = ?
    """
    return fetch_one(db, query, [party_id, drink])


def add_or_update_drink_name_and_cost(db, drink_name, drink_cost):
    """Add a drink to a party, or update the cost if it already exists."""
    party_id = current_user.id
    query = """
        select drink_name
        from drinks
        where party_id = ?
            and drink_name = ?
    """
    drinks = db.execute(query, [party_id, drink_name]).fetchall()

    if drink_name in [row[0] for row in drinks]:
        # update existing drink with new price
        query = """
            update drinks
            set drink_cost = ?
            where party_id = ?
                and drink_name = ?
        """
        db.execute(query, [drink_cost, party_id, drink_name])
    else:
        # insert new drink
        query = "insert into drinks (party_id, drink_name, drink_cost) values (?, ?, ?)"
        db.execute(query, [party_id, drink_name, drink_cost])
    
    db.commit()