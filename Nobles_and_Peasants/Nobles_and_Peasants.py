# all the imports
import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

# create the application instance and load config
app = Flask(__name__)
app.config.from_object(__name__)

# load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flask_test.db'),
    SECRET_KEY='development_key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASK_TEST_SETTINGS', silent=True)

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')


def get_db():
    """Opens a new database connection if there is none yet
    for the current application context
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/rules')
def show_rules():
    return render_template('rules.html')

@app.route('/main')
def start_game():
    return render_template('main.html')

@app.route('/main')
def show_main():
    return render_template('main.html')

@app.route('/main', methods=['POST'])
def sign_in():
    return redirect(url_for('show_main'))

@app.route('/main', methods=['POST'])
def pledge_allegiance():
    return redirect(url_for('show_main'))

@app.route('/main', methods=['POST'])
def buy_drink():
    return redirect(url_for('show_main'))

@app.route('/main', methods=['POST'])
def ban_peasant():
    return redirect(url_for('show_main'))

@app.route('/main', methods=['POST'])
def get_dare():
    return redirect(url_for('show_main'))

@app.route('/main', methods=['POST'])
def kill():
    return redirect(url_for('show_main'))

@app.route('/kingdom')
def show_kingdom():
    query = 'select id, status, coin, allegiance, drinks, soldiers from kingdom order by allegiance, coin desc, soldiers desc'
    db = get_db()
    kingdom = db.execute(query).fetchall()
    return render_template('show_kingdom.html', kingdom=kingdom)

@app.route('/leaderboard')
def show_leaderboard():
    query = "select id, soldiers, coin from kingdom where status = 'noble' order by soldiers desc, coin desc"
    db = get_db()
    leaderboard = db.execute(query).fetchall()
    return render_template('show_leaderboard.html', leaderboard=leaderboard)
