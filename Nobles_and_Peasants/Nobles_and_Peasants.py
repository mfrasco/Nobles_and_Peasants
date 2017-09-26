# all the imports
import os
import sqlite3
from flask import (
    Flask,
    request,
    g,
    redirect,
    url_for,
    render_template,
    flash
)
from flask_login import LoginManager, UserMixin
from random import uniform
from Nobles_and_Peasants.nap_helpers import (
    fetch_one,
    get_starting_info,
    find_richest_peasant,
    decrement_previous_noble,
    switch_allegiances,
    update_new_noble,
    make_noble_peasant,
    take_money,
    n_beats_p,
    p_beats_n,
    n_beats_n
)

# create the application instance and load config
app = Flask(__name__, instance_relative_config=True)
app.config.from_object('Nobles_and_Peasants.default_settings')
app.config.from_pyfile('application.cfg', silent=True)

# # handle the login manager
# login_manager = LoginManager()
# login_manager.init_app(app)

# @login_manager.user_loader
# def load_user(user_id):
#     return User.get(user_id)

############################################################
################# Setup Database ########################
############################################################


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


############################################################
################# Show setup pages ########################
############################################################

@app.route('/')
def show_login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    party_id = request.form['party_id']
    # password = request.form['password']
    init_db()
    return redirect(url_for('welcome'))

@app.route('/set_up', methods=['GET'])
def welcome():
    db = get_db()
    drinks = db.execute('select * from drinks order by coin').fetchall()
    starting_coin = db.execute('select * from starting_coin').fetchall()
    wages = db.execute('select * from wages').fetchall()
    return render_template('welcome.html', drinks = drinks, starting_coin = starting_coin, wages = wages)

@app.route('/rules')
def show_rules():
    return render_template('rules.html')

############################################################
################# Setup Party ########################
############################################################

@app.route('/add_drink', methods=['POST'])
def add_drink():
    db = get_db()
    drink_name = request.form['drink_name'].strip().lower()
    price = int(request.form['price'])

    if drink_name == 'water' and price >= 0:
        flash('Unsuccessful! Water must have a negative price.')
        return redirect(url_for('welcome'))

    query = 'replace into drinks (name, coin) values (?, ?)'
    db.execute(query, [drink_name, price])
    db.commit()
    return redirect(url_for('welcome'))

@app.route('/set_coin', methods=['POST'])
def set_coin():
    db = get_db()
    noble_coin = int(request.form['noble_coin'])
    query = 'update starting_coin set coin = ? where status = ?'
    db.execute(query, [noble_coin, 'noble'])
    db.commit()
    return redirect(url_for('welcome'))

@app.route('/set_wages', methods=['POST'])
def set_wages():
    easy_wage = int(request.form['easy'])
    medium_wage = int(request.form['medium'])
    hard_wage = int(request.form['hard'])

    if medium_wage < easy_wage:
        flash('Medium reward cannot be less than easy reward')
        return redirect(url_for('welcome'))

    if hard_wage < medium_wage:
        flash('Hard reward cannot be less than medium reward')
        return redirect(url_for('welcome'))

    db = get_db()
    query = '''
    update wages set coin = (case when level = ? then ?
                                  when level = ? then ?
                                  else ?
                             end)
    '''

    db.execute(query, ['easy', easy_wage, 'medium', medium_wage, hard_wage])
    db.commit()
    return redirect(url_for('welcome'))

############################################################
################# Show main page ########################
############################################################

@app.route('/main')
def show_main():
    db = get_db()
    # get drink names
    query = 'select name from drinks order by coin'
    drinks = db.execute(query).fetchall()
    drinks = [d[0] for d in drinks]

    # get people names
    query = 'select id from kingdom order by id'
    people = db.execute(query).fetchall()
    people = [p[0] for p in people]

    # get noble names
    query = 'select id from kingdom where status = ? order by id'
    nobles = db.execute(query, ['noble']).fetchall()
    nobles = [n[0] for n in nobles]

    return render_template('main.html', drinks = drinks, people = people, nobles = nobles)

############################################################
################# Sign In ########################
############################################################

@app.route('/sign_in', methods=['POST'])
def sign_in():
    user_id = request.form['user_id'].strip().lower()
    user_status = request.form['user_status']
    db = get_db()

    # check that the id is not already taken
    current_ids = db.execute('select id from kingdom').fetchall()
    if user_id in [row[0] for row in current_ids]:
        flash('Unsuccessful! Please choose a different id. Someone already selected that one.')
        return redirect(url_for('show_main'))

    if user_status == 'randomly decide':
        statuses = db.execute('select status from kingdom').fetchall()
        statuses = [s[0] for s in statuses]
        num_people = len(statuses)
        num_nobles = statuses.count('noble')
        if num_nobles < 2:
            user_status =  'noble'
        elif (float(num_nobles) / num_people) < 0.2:
            if uniform(0, 1) < 0.75:
                user_status = 'noble'
            else:
                user_status = 'peasant'
        else:
            user_status = 'peasant'

    start_info = get_starting_info(db, user_status, user_id)

    starting_coin, allegiance, soldiers = start_info
    db.execute('insert into kingdom (id, status, coin, allegiance, drinks, soldiers) values (?, ?, ?, ?, ?, ?)',
               [user_id, user_status, starting_coin, allegiance, 0, soldiers])
    db.commit()
    return redirect(url_for('show_main'))

############################################################
################# Pledge Allegiance ########################
############################################################

@app.route('/pledge', methods=['POST'])
def pledge_allegiance():
    user_id = request.form['user_id'].strip().lower()
    noble_id = request.form['noble_id'].strip().lower()

    db = get_db()

    # check the request values are valid
    query = 'select status from kingdom where id = ?'
    user_status = fetch_one(db, query, [user_id])
    noble_status = fetch_one(db, query, [noble_id])

    # error checking
    if user_status is None:
        flash('Unsuccessful! Please enter a valid id for yourself. Have you signed in?')
        return redirect(url_for('show_main'))

    if noble_status is None:
        flash('Unsuccessful! Please enter a valid id for the noble.')
        return redirect(url_for('show_main'))

    if noble_status != 'noble':
        flash('Unsuccessful! That person is not a noble')
        return redirect(url_for('show_main'))

    if user_status == 'noble':
        flash('Unsuccessful! You are a noble. You must be allied to yourself.')
        return redirect(url_for('show_main'))

    # check if noble has banned peasant
    query = 'select outlaw from banned where noble = ?'
    outlaws = db.execute(query, [noble_id]).fetchall()
    outlaws = [x[0] for x in outlaws]
    if len(outlaws) > 0 and user_id in outlaws[0]:
        flash('Unsuccessful! This noble has banned you from their kingdom!')
        return redirect(url_for('show_main'))

    # update the allegiance in the database
    query = 'select allegiance from kingdom where id = ?'
    previous_noble = fetch_one(db, query, [user_id])
    db.execute('update kingdom set allegiance = ? where id = ?', [noble_id, user_id])
    db.execute('update kingdom set soldiers = soldiers + 1 where id = ?', [noble_id])
    
    if previous_noble is not None:
        db.execute('update kingdom set soldiers = soldiers - 1 where id = ?', [previous_noble])

    db.commit()
    return redirect(url_for('show_main'))

############################################################
################# Buy a Drink ########################
############################################################

@app.route('/buy_drink', methods=['POST'])
def buy_drink():
    user_id = request.form['user_id'].strip().lower()
    drink = request.form['drink']
    quantity = int(request.form['quantity'])

    db = get_db()

    # check noble status
    query = 'select allegiance from kingdom where id = ?'
    noble_id = fetch_one(db, query, [user_id])
    if noble_id is None:
        flash('Unsuccessful! You need to ally yourself to a noble before you can buy a drink.')
        return redirect(url_for('show_main'))

    query = 'select coin from drinks where name = ?'
    price = fetch_one(db, query, [drink])
    cost = price * quantity

    # cut out for water
    if drink == 'water':
        query = 'update kingdom set coin = coin - ? where id = ?'
        db.execute(query, [cost, user_id])
        db.commit()
        return redirect(url_for('show_main'))

    # If the noble has enough money, take it. If not, create a new noble.
    query = 'select coin from kingdom where id = ?'
    noble_coin = fetch_one(db, query, [noble_id])

    db.execute('update kingdom set coin = ? where id = ?', [max(noble_coin - cost, 0), noble_id])
    db.execute('update kingdom set drinks = drinks + ? where id = ?', [quantity, user_id])

    if noble_coin <= cost:
        new_noble = find_richest_peasant(db = db)
        decrement_previous_noble(db = db, new_noble = new_noble)
        switch_allegiances(db = db, new_noble = new_noble, old_noble = noble_id)
        update_new_noble(db = db, new_noble = new_noble)
        make_noble_peasant(db = db, old_noble = noble_id)

    db.commit()

    return redirect(url_for('show_main'))

############################################################
################# Ban a Peasant ########################
############################################################

@app.route('/ban', methods=['POST'])
def ban_peasant():
    noble_id = request.form['noble_id'].strip().lower()
    peasant_id = request.form['peasant_id'].strip().lower()

    db = get_db()

    # check input validity
    query = 'select status from kingdom where id = ?'
    noble_status = fetch_one(db, query, [noble_id])

    if noble_status is None:
        flash('Unsuccessful! Unknown id. Did you enter your id correctly?')
        return redirect(url_for('show_main'))

    if noble_status != 'noble':
        flash('Unsuccessful! You are not a noble. You cannot ban people from kingdom you do not have.')
        return redirect(url_for('show_main'))

    query = 'select allegiance from kingdom where id = ?'
    peasant_allegiance = fetch_one(db, query, [peasant_id])
    if peasant_allegiance is None:
        flash('Unsuccessful! The peasant id that you entered does not exist.')
        return redirect(url_for('show_main'))

    # remove the peasant's allegiance to the noble that is banning her
    if peasant_allegiance == noble_id:
        db.execute('update kingdom set allegiance = ? where id = ?', [None, peasant_id])
        db.execute('update kingdom set soldiers = soldiers - 1 where id = ?', [noble_id])

    # add the peasant to a banned table
    db.execute('insert into banned (noble, outlaw) values (?, ?)', [noble_id, peasant_id])
    db.commit()
    return redirect(url_for('show_main'))

############################################################
################# Get a Quest ########################
############################################################

@app.route('/get_quest', methods=['POST'])
def get_quest():
    user_id = request.form['user_id'].strip().lower()
    level = request.form['level'].strip().lower()

    db = get_db()
    query = 'select id from kingdom where id = ?'
    user_id = fetch_one(db, query, [user_id])

    if user_id is None:
        flash('Unsuccessful! You entered a bad id.')

    query = 'select quest from quests where level = ? order by random() limit 1'
    quest = fetch_one(db, query, [level])
    return render_template('quest.html', id = user_id, level = level, quest = quest)

@app.route('/add_money', methods=['POST'])
def add_money():
    user_id = request.form['user_id'].strip().lower()
    level = request.form['level']
    result = request.form['result']

    if result == 'Yes':
        db = get_db()
        query = 'update kingdom set coin = coin + (select coin from wages where level = ?) where id = ?'
        db.execute(query, [level, user_id])
        db.commit()

    return redirect(url_for('show_main'))

############################################################
################# Kill a Peasant ########################
############################################################

@app.route('/kill', methods=['POST'])
def kill():
    user_id = request.form['user_id'].strip().lower()
    target_id = request.form['target_id'].strip().lower()
    db = get_db()

    query = 'select coin, status from kingdom where id = ?'
    user_info = db.execute(query, [user_id]).fetchone()
    target_info = db.execute(query, [target_id]).fetchone()

    if user_info is None:
        flash('Unsuccessful! You entered a bad id for yourself')
        return redirect(url_for('show_main'))

    if target_info is None:
        flash('Unsuccessful! You entered a bad id for your target')
        return redirect(url_for('show_main'))

    user_coin, user_status = user_info
    target_coin, target_status = target_info

    if user_status == 'peasant' and target_status == 'noble':
        query = 'select coin from starting_coin where status = ?'
        coin_needed = fetch_one(db, query, ['noble'])
        if user_coin < coin_needed:
            flash('Unsuccessful! You do not have enough coin to assassinate a noble.')
            return redirect(url_for('show_main'))

    query = 'select challenge from challenges order by random() limit 1'
    challenge = fetch_one(db, query, [])

    return render_template('kill.html', challenge = challenge, user_id = user_id, target_id = target_id)

@app.route('/assassinate', methods=['POST'])
def assassinate():
    user_id = request.form['user_id']
    target_id = request.form['target_id']
    winner = request.form['winner']
    db = get_db()

    if user_id == winner:
        loser = target_id
    else:
        loser = user_id

    query = 'select status from kingdom where id = ?'
    winner_status = fetch_one(db, query, [winner])
    loser_status = fetch_one(db, query, [loser])

    if winner_status == 'peasant' and loser_status == 'peasant':
        take_money(db, winner, loser)
    elif winner_status == 'peasant' and loser_status == 'noble':
        p_beats_n(db, winner, loser)
    elif winner_status == 'noble' and loser_status == 'peasant':
        n_beats_p(db, winner, loser)
    else:
        n_beats_n(db, winner, loser)

    db.commit()

    return redirect(url_for('show_main'))

############################################################
################# View the Database ########################
############################################################

@app.route('/kingdom')
def show_kingdom():
    query = '''
    select id, status, coin, allegiance, drinks, soldiers
    from kingdom
    order by allegiance, coin desc, drinks desc, id
    '''
    db = get_db()
    kingdom = db.execute(query).fetchall()
    return render_template('show_kingdom.html', kingdom = kingdom)

@app.route('/leaderboard')
def show_leaderboard():
    query = '''
    select id, soldiers, coin, drinks
    from kingdom
    where status = 'noble'
    order by soldiers desc, coin desc, drinks desc
    '''
    db = get_db()
    leaderboard = db.execute(query).fetchall()
    query = 'select id from kingdom order by soldiers desc limit 1'
    almighty_ruler = fetch_one(db, query, [])
    return render_template('show_leaderboard.html'
                           , leaderboard = leaderboard
                           , almighty_ruler = almighty_ruler)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
