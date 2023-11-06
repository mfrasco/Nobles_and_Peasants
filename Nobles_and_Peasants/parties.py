"""Functions related to the parties table."""
import re

from flask_bcrypt import generate_password_hash

from Nobles_and_Peasants.query import fetch_one


def init_party(app, db, party_id):
    """Add rows to tables in the schema with default content for this party."""
    with app.open_resource("default_values.sql", mode="r") as f:
        schema = f.read()
        schema = re.sub("~PARTY_ID~", party_id, schema)
        db.cursor().executescript(schema)
    db.commit()


def does_party_id_exist(db, party_id):
    """Check if a party_id already exists in the database."""
    query = "select party_id from parties"
    parties = db.execute(query).fetchall()
    return party_id in [row[0] for row in parties]


def insert_new_party(app, db, party_id, password):
    """Add a row to the database for a new party."""
    hashed_password = generate_password_hash(password, rounds=12)

    query = "insert into parties (party_id, password) values (?, ?)"
    db.execute(query, [party_id, hashed_password])
    init_party(app=app, db=db, party_id=party_id)
    db.commit()


def get_hashed_password(db, party_id):
    """Get the hashed password for a party."""
    query = "select password from parties where party_id = ?"
    return fetch_one(db, query, [party_id])
