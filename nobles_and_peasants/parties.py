"""Functions related to the parties table."""
import re

from flask import current_app
from werkzeug.security import generate_password_hash

from nobles_and_peasants.db import get_db
from nobles_and_peasants.query import execute, fetch_one, fetch_all


def init_party(party_id):
    """Add rows to tables in the schema with default content for this party."""
    db = get_db()
    with current_app.open_resource("default_values.sql") as f:
        default_values = f.read().decode("utf8")
        default_values = re.sub("~PARTY_ID~", str(party_id), default_values)
        db.executescript(default_values)
    db.commit()


def insert_new_party(party_name, password):
    """Add a row to the database for a new party."""
    hashed_password = generate_password_hash(password)

    query = "insert into parties (party_name, password) values (?, ?)"
    execute(query=query, args=[party_name, hashed_password], commit=True)

    party_id = get_party_id(party_name=party_name)
    init_party(party_id=party_id)


def get_party(party_name):
    """Get info for a party."""
    query = "select id, party_name, password from parties where party_name = ?"
    party = fetch_all(query=query, args=[party_name])
    if len(party) == 0:
        return None
    else:
        return party[0]


def get_party_id(party_name):
    """Get the id given the party name."""
    query = "select id from parties where party_name = ?"
    return fetch_one(query=query, args=[party_name])


def get_party_name(db, party_id):
    """Get the party_name given the party_id."""
    query = "select party_name from parties where id = ?"
    return fetch_one(db, query, [party_id])


def does_party_id_exist(party_id):
    """Check if a party_id already exists in the database."""
    query = "select id from parties"
    parties = fetch_all(query=query)
    return int(party_id) in [row["id"] for row in parties]


def does_party_name_exist(party_name):
    """Check if a party_name already exists in the database."""
    query = "select party_name from parties"
    parties = fetch_all(query=query)
    return party_name in [row["party_name"] for row in parties]
