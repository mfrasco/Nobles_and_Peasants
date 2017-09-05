# all the imports
import os
import sqlite3
from flask import (
    Flask,
    request,
    session,
    g,
    redirect,
    url_for,
    abort,
    render_template,
    flash
)
from random import randint, uniform

# create the application instance and load config
app = Flask(__name__)
app.config.from_object(__name__)

# load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'nobles_and_peasants.db'),
    SECRET_KEY='development_key',
    USERNAME='admin',
    PASSWORD='default',
    DEBUG=True
))
app.config.from_envvar('NOBLES_AND_PEASANTS_SETTINGS', silent=True)

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

# Helper functions
def fetch_one(query_string, args):
    db = get_db()
    return db.execute(query_string, args).fetchone()

@app.route('/', methods=['GET'])
def welcome():
    db = get_db()
    drinks = db.execute('select * from drinks').fetchall()
    starting_coin = db.execute('select * from starting_coin').fetchall()
    return render_template('welcome.html', drinks=drinks, starting_coin=starting_coin)

@app.route('/rules')
def show_rules():
    return render_template('rules.html')

@app.route('/add_drink', methods=['POST'])
def add_drink():
    db = get_db()
    drink_name = request.form['drink_name']
    price = request.form['price']
    query = 'insert into drinks values (?, ?)'
    db.execute(query, [drink_name, price])
    db.commit()
    return redirect(url_for('welcome'))

@app.route('/set_coin', methods=['POST'])
def set_coin():
    db = get_db()
    noble_coin = request.form['noblecoin']
    query = 'update starting_coin set coin = ? where status = ?'
    db.execute(query, [noble_coin, 'noble'])
    db.commit()
    return redirect(url_for('welcome'))

@app.route('/main')
def show_main():
    return render_template('main.html')

def get_starting_info(status, user_id):
    query = 'select coin from starting_coin where status = ?'
    starting_coin = db.execute(query, [status]).fetchone()
    if status = 'peasant':
        allegiance = None
        soldiers = 0
    else:
        allegiance = user_id
        soldiers = 1
    return starting_coin, allegiance, soldiers

@app.route('/main', methods=['POST'])
def sign_in():
    user_id = request.form['user_id']
    user_status = request.form['user_status']
    db = get_db()

    # check that the id is not already taken
    current_ids = db.execute('select id from kingdom').fetchall()
    if user_id in current_ids:
        error = 'Please choose a different id. Someone already has this one.'
        return render_template('error.html', error = error, image = 'oops.jpg')

    if user_status = 'randomly decide':
        statuses = db.execute('select status from kingdom').fetchall()
        num_people = len(statuses)
        if num_people == 0:
            starting_coin, allegiance, soldiers = get_starting_info('noble', user_id)
        elif (num_nobles / num_people) < 0.2:
            if random_num < 0.5:
                starting_coin, allegiance, soldiers = get_starting_info('noble', user_id)
            else:
                starting_coin, allegiance, soldiers = get_starting_info('peasant', user_id)
        else:
            starting_coin, allegiance, soldiers = get_starting_info('peasant', user_id)

        num_nobles = statuses.count('noble')

    else:
        starting_coin, allegiance, soldiers = get_starting_info(user_status, user_id)

    db.execute('insert into kingdom (id, status, coin, allegiance, drinks, soldiers) values (?, ?, ?, ?, ?, ?)',
               [user_id, user_status, coin, allegiance, 0, soldiers])
    db.commit()
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


if __name__ == '__main__':
    app.run(host='0.0.0.0')

