import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash

from nobles_and_peasants.db import get_db
from nobles_and_peasants.parties import does_party_name_exist, insert_new_party, get_party


bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/signup', methods=('GET', 'POST'))
def signup():
    if request.method == 'POST':
        party_name = request.form['party_name']
        password = request.form['password']
        db = get_db()

        if does_party_name_exist(db=db, party_name=party_name):
            msg = f"Unsuccessful! Please choose a different party name. Someone already selected {party_name}."
            flash(msg)
            return render_template("login.html", party_name=None)

        insert_new_party(db=db, party_name=party_name, password=password)
        flash("Success! You can now log in to your party!")
        return render_template("login.html", party_name=party_name)


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        party_name = request.form["party_name"]
        password = request.form["password"]
        db = get_db()

        party = get_party(db=db, party_name=party_name)

        if party is None:
            msg = f"Unsuccessful! {party_name} has not been registered yet. Please sign up to create a party."
            flash(msg)
            return render_template("login.html", party_name=None)

        if not check_password_hash(pwhash=party["password"], password=password):
            msg = f"Unsuccessful! That is not the correct password for {party_name}."
            flash(msg)
            return render_template("login.html", party_name=None)

        session.clear()
        session['party_id'] = party["id"]
        session['party_name'] = party_name
        return redirect(url_for("what_is_this"))

    return render_template("login.html", party_name=None)


@bp.before_app_request
def load_logged_in_user():
    party_id = session.get('party_id')
    party_name = session.get('party_name')

    if party_id is None:
        g.user = None
    else:
        g.user = {"party_id": party_id, "party_name": party_name}


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("show_login"))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

