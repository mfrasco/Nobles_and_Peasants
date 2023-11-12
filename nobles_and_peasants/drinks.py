"""Functions related to the drinks table."""
from flask import session

from nobles_and_peasants.query import execute, fetch_all, fetch_one


def get_drink_name_and_cost():
    """Get all drink names and costs."""
    party_id = session.get("party_id")
    query = """
        select drink_name, drink_cost
        from drinks
        where party_id = ?
        order by drink_cost
    """
    return fetch_all(query=query, args=[party_id])


def get_cost_for_a_drink(drink_name):
    """Get the cost for a single drink."""
    party_id = session.get("party_id")
    query = """
        select drink_cost
        from drinks
        where party_id = ?
            and drink_name = ?
    """
    return fetch_one(query=query, args=[party_id, drink_name])


def add_or_update_drink_name_and_cost(drink_name, drink_cost, commit):
    """Add a drink to a party, or update the cost if it already exists."""
    party_id = session.get("party_id")
    query = """
        select drink_name
        from drinks
        where party_id = ?
            and drink_name = ?
    """
    drinks = fetch_all(query=query, args=[party_id, drink_name])

    if drink_name in [row["drink_name"] for row in drinks]:
        # update existing drink with new price
        query = """
            update drinks
            set drink_cost = ?
            where party_id = ?
                and drink_name = ?
        """
        execute(query=query, args=[drink_cost, party_id, drink_name], commit=commit)
    else:
        # insert new drink
        query = "insert into drinks (party_id, drink_name, drink_cost) values (?, ?, ?)"
        execute(query=query, args=[party_id, drink_name, drink_cost], commit=commit)
