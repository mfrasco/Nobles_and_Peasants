"""Functions related to the parties table."""
import re

from flask import current_app
from werkzeug.security import generate_password_hash

from nobles_and_peasants.query import fetch_one


def init_party(db, party_id):
    """Add rows to tables in the schema with default content for this party."""
    with current_app.open_resource("default_values.sql") as f:
        default_values = f.read().decode("utf8")
        default_values = re.sub("~PARTY_ID~", str(party_id), default_values)
        db.executescript(default_values)
    db.commit()


def insert_new_party(db, party_name, password):
    """Add a row to the database for a new party."""
    hashed_password = generate_password_hash(password)

    query = "insert into parties (party_name, password) values (?, ?)"
    db.execute(query, [party_name, hashed_password])

    party_id = get_party_id(db=db, party_name=party_name)
    init_party(db=db, party_id=party_id)
    db.commit()


def get_party(db, party_name):
    """Get info for a party."""
    query = "select id, party_name, password from parties where party_name = ?"
    party = db.execute(query, [party_name]).fetchall()
    if len(party) == 0:
        return None
    else:
        return party[0]


def get_party_id(db, party_name):
    """Get the id given the party name."""
    query = "select id from parties where party_name = ?"
    return fetch_one(db, query, [party_name])


def get_party_name(db, party_id):
    """Get the party_name given the party_id."""
    query = "select party_name from parties where id = ?"
    return fetch_one(db, query, [party_id])


def does_party_id_exist(db, party_id):
    """Check if a party_id already exists in the database."""
    query = "select id from parties"
    parties = db.execute(query).fetchall()
    return int(party_id) in [row["id"] for row in parties]


def does_party_name_exist(db, party_name):
    """Check if a party_name already exists in the database."""
    query = "select party_name from parties"
    parties = db.execute(query).fetchall()
    return party_name in [row["party_name"] for row in parties]
