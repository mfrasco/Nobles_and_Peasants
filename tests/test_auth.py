"""Tests for authentication ability."""
import pytest
from flask import g, session
from nobles_and_peasants.db import get_db


def test_signup(client, app):
    """Test that signing up a new party creates a row in the database."""
    assert client.get('/auth/signup').status_code == 200
    
    data = {'party_name': 'test_signup_name', 'password': 'test_signup_pw'}
    client.post('/auth/signup', data=data)

    with app.app_context():
        db = get_db()
        query = "SELECT * FROM parties WHERE party_name = 'test_signup_name'"
        assert db.execute(query).fetchone() is not None


@pytest.mark.parametrize(
    ('party_name', 'password', 'message'),
    (
        ('', 'pw', b'Unsuccessful! You must choose a name for your party.'),
        ('pn', '', b'Unsuccessful! You must choose a password for your party.'),
        ('party_name_1', 'pw', b'Unsuccessful! Please choose a different party name. Someone already selected party_name_1.'),
    )
)
def test_signup_validate_input(client, party_name, password, message):
    """Test that signup handles errors correctly."""
    response = client.post(
        '/auth/signup',
        data={'party_name': party_name, 'password': password}
    )
    assert message in response.data


def test_login(client, auth):
    """Test that logging in to a party sets session variables correctly."""
    assert client.get('/auth/login').status_code == 200
    response = auth.login(party_name="party_name_1", password="maya")
    assert 'What is Nobles and Peasants?' in response.text

    with client:
        client.get('/')
        assert session['party_id'] == 1
        assert g.user['party_name'] == 'party_name_1'


@pytest.mark.parametrize(
    ('party_name', 'password', 'message'),
    (
        ('unknown_party_name', 'test', b'Unsuccessful! unknown_party_name has not been registered yet. Please sign up to create a party.'),
        ('party_name_1', 'a', b'Unsuccessful! That is not the correct password for party_name_1.'),
    )
)
def test_login_validate_input(auth, party_name, password, message):
    """Test that login errors are handled properly."""
    response = auth.login(party_name, password)
    assert message in response.data


def test_logout(client, auth):
    """Test that logging out clears session variables."""
    auth.login(party_name="party_name_1", password="maya")

    with client:
        auth.logout()
        assert 'party_id' not in session
        assert 'party_name' not in session
