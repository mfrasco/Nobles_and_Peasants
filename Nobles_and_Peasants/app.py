"""Flask app for running Nobles and Peasants."""
from flask import Flask, request, g, redirect, url_for, render_template, flash
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_user,
    logout_user,
    login_required,
)
from flask_bcrypt import check_password_hash
import sqlite3

from nobles_and_peasants.challenges import get_random_challenge
from nobles_and_peasants.constants import NOBLE, PEASANT
from nobles_and_peasants.drinks import (
    add_or_update_drink_name_and_cost,
    get_cost_for_a_drink,
    get_drink_name_and_cost,
)
from nobles_and_peasants.outlaws import (
    is_peasant_banned,
    insert_new_outlaw,
)
from nobles_and_peasants.parties import (
    does_party_id_exist,
    get_hashed_password,
    insert_new_party,
)
from nobles_and_peasants.players import (
    find_richest_peasant,
    get_all_nobles,
    get_all_players,
    get_almighty_ruler,
    get_single_player,
    increment_coin,
    increment_drinks,
    increment_soldiers,
    insert_new_player,
    move_coin_between_players,
    randomly_choose_player_status,
    update_after_pledge_allegiance,
    upgrade_peasant_and_downgrade_noble,
    set_allegiance,
)
from nobles_and_peasants.starting_coin import (
    get_status_and_starting_coin,
    get_starting_coin_for_status,
    update_noble_starting_coin,
)
from nobles_and_peasants.quests import get_random_quest
from nobles_and_peasants.quest_rewards import (
    get_quest_difficulty_and_reward,
    get_reward_for_difficulty,
    set_quest_rewards,
)


# create the application instance and load config
app = Flask(__name__)
app.secret_key = "super secret key"

# app = Flask(__name__, instance_relative_config=True)
# app.config.from_object('nobles_and_peasants.default_settings')
# app.config.from_pyfile('application.cfg', silent=True)

############################################################
################# Setup Database ########################
############################################################


def connect_db():
    """Connects to the specific database."""
    # rv = sqlite3.connect(app.config['DATABASE'])
    rv = sqlite3.connect("nap.db")
    rv.row_factory = sqlite3.Row
    return rv


def get_db():
    """Opens a new database connection if there is none yet for the current app context."""
    if not hasattr(g, "sqlite_db"):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database at the end of the request."""
    if hasattr(g, "sqlite_db"):
        g.sqlite_db.close()


def init_db():
    """Initialize database by executing SQL script."""
    db = get_db()
    with app.open_resource("schema.sql", mode="r") as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command("initdb")
def initdb_command():
    """Initializes the database."""
    init_db()
    print("Initialized the database.")


############################################################
################# User Handling ######################
############################################################


class User(UserMixin):
    """User class."""

    def __init__(self, id):
        """Initialize the user."""
        self.id = id

    def get_id(self):
        """Get the user id."""
        return str(self.id)


# handle the login manager
login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = "show_login"


@login_manager.user_loader
def load_user(party_id):
    """Load user."""
    db = get_db()

    if not does_party_id_exist(db=db, party_id=party_id):
        return None

    user = User(party_id)
    return user


############################################################
################# Show setup pages ########################
############################################################


@app.route("/")
def show_login():
    """Show the login page."""
    if current_user.is_authenticated:
        party_id = current_user.id
    else:
        party_id = None
    return render_template("login.html", party_id=party_id)


@app.route("/how_to_play")
def how_to_play():
    """Show the how to play page."""
    if current_user.is_authenticated:
        party_id = current_user.id
    else:
        party_id = None
    return render_template("how_to_play.html", party_id=party_id)


@app.route("/what_is_this")
def what_is_this():
    """Show the what is this page."""
    if current_user.is_authenticated:
        party_id = current_user.id
    else:
        party_id = None
    return render_template("what_is_this.html", party_id=party_id)


@app.route("/signup", methods=["POST"])
def signup():
    """Process the party_id and the password when the user registers a new party."""
    party_id = request.form["party_id"]
    password = request.form["password"]

    db = get_db()

    if does_party_id_exist(db=db, party_id=party_id):
        msg = f"Unsuccessful! Please choose a different party name. Someone already selected {party_id}."
        flash(msg)
        return redirect(url_for("show_login"))

    insert_new_party(app=app, db=db, party_id=party_id, password=password)
    flash("Success! You can now log in to your party!")
    return redirect(url_for("show_login"))


@app.route("/login", methods=["POST"])
def login():
    """Process the users request to login to their party."""
    party_id = request.form["party_id"]
    password = request.form["password"]

    db = get_db()
    hashed_password = get_hashed_password(db=db, party_id=party_id)

    if hashed_password is None:
        msg = f"Unsuccessful! Party ID: {party_id} has not been registered yet. Please sign up to create a party."
        flash(msg)
        return redirect(url_for("show_login"))

    if not check_password_hash(hashed_password, password):
        msg = (
            f"Unsuccessful! That is not the correct password for Party ID: {party_id}."
        )
        flash(msg)
        return redirect(url_for("show_login"))

    user = User(party_id)
    login_user(user)

    next = request.args.get("next")
    # if not is_safe_url:
    #     flash('Unsuccessful! What is going on?')
    #     return(redirect(url_for('show_login')))

    return redirect(next or url_for("what_is_this"))


@app.route("/logout")
def logout():
    """Logout the user."""
    logout_user()
    return redirect(url_for("show_login"))


@app.route("/set_up", methods=["GET"])
@login_required
def set_up():
    """Show the setup page, where the user can customize the party settings."""
    db = get_db()

    party_id = current_user.id

    drinks = get_drink_name_and_cost(db=db)
    starting_coin = get_status_and_starting_coin(db=db)
    quest_rewards = get_quest_difficulty_and_reward(db=db)

    return render_template(
        "setup.html",
        drinks=drinks,
        starting_coin=starting_coin,
        quest_rewards=quest_rewards,
        party_id=party_id,
    )


@app.route("/rules")
def show_rules():
    """Show the page that describes the rules."""
    return render_template("rules.html")


############################################################
################# Setup Party ########################
############################################################


@app.route("/add_drink", methods=["POST"])
def add_drink():
    """Process request to add a drink to the party."""
    db = get_db()
    drink_name = request.form["drink_name"].strip().lower()
    price = int(request.form["price"])

    add_or_update_drink_name_and_cost(db=db, drink_name=drink_name, drink_cost=price)
    return redirect(url_for("set_up"))


@app.route("/set_coin", methods=["POST"])
def set_coin():
    """Respond to request to set starting coin for each role."""
    db = get_db()
    noble_coin = int(request.form["noble_coin"])
    update_noble_starting_coin(db=db, noble_coin=noble_coin)
    return redirect(url_for("set_up"))


@app.route("/set_wages", methods=["POST"])
def set_wages():
    """Respond to a request to set rewards for quests."""
    easy_reward = int(request.form["easy"])
    medium_reward = int(request.form["medium"])
    hard_reward = int(request.form["hard"])

    if medium_reward < easy_reward:
        flash("Medium reward cannot be less than easy reward")
        return redirect(url_for("set_up"))

    if hard_reward < medium_reward:
        flash("Hard reward cannot be less than medium reward")
        return redirect(url_for("set_up"))

    db = get_db()
    set_quest_rewards(
        db=db,
        easy_reward=easy_reward,
        medium_reward=medium_reward,
        hard_reward=hard_reward,
    )

    return redirect(url_for("set_up"))


############################################################
################# Show main page ########################
############################################################


@app.route("/main")
@login_required
def show_main():
    """Display the main page."""
    db = get_db()
    party_id = current_user.id

    drinks = get_drink_name_and_cost(db=db)
    drink_names = [row["drink_name"] for row in drinks]

    players = get_all_players(db=db)
    player_names = [row["player_name"] for row in players]
    noble_names = [row["player_name"] for row in players if row["player_status"] == NOBLE]

    return render_template(
        "main.html",
        drink_names=drink_names,
        player_names=player_names,
        noble_names=noble_names,
        party_id=party_id,
    )


############################################################
################# Sign In ########################
############################################################


@app.route("/sign_in", methods=["POST"])
def sign_in():
    """Process a users request to sign in to the game."""
    player_name = request.form["player_name"].strip().lower()
    player_status = request.form["player_status"]

    db = get_db()
    players = get_all_players(db=db)

    existing_players = [row["player_name"] for row in players]
    if player_name in existing_players:
        msg = f"Unsuccessful! Please choose a different name. Someone already selected {player_name}."
        flash(msg)
        return redirect(url_for("show_main"))

    if player_status == "randomly decide":
        status = randomly_choose_player_status(players=players)
    else:
        status = player_status

    insert_new_player(db=db, player_name=player_name, player_status=status)

    return redirect(url_for("show_main"))


############################################################
################# Pledge Allegiance ########################
############################################################


@app.route("/pledge", methods=["POST"])
def pledge_allegiance():
    """Process the request to pledge allegiance to a noble."""
    player_name = request.form["player_name"].strip().lower()
    noble_name = request.form["noble_name"].strip().lower()

    db = get_db()
    player = get_single_player(db=db, player_name=player_name)
    noble = get_single_player(db=db, player_name=noble_name)

    if player["player_status"] is None:
        msg = f"Unsuccessful! Please enter a valid name for yourself. You entered: {player_name}. Have you signed in?"
        flash(msg)
        return redirect(url_for("show_main"))

    if noble["player_status"] is None:
        msg = f"Unsuccessful! Please enter a valid name for the noble. You entered: {noble_name}."
        flash(msg)
        return redirect(url_for("show_main"))

    if noble["player_status"] != NOBLE:
        msg = f"Unsuccessful! {noble_name} is not a noble."
        flash(msg)
        return redirect(url_for("show_main"))

    if player["player_status"] == NOBLE:
        msg = f"Unsuccessful! {player_name} is a noble. You must be allied to yourself."
        flash(msg)
        return redirect(url_for("show_main"))

    if is_peasant_banned(db=db, noble_id=noble["id"], peasant_id=player["id"]):
        msg = f"Unsuccessful! {noble_name} has banned you from their kingdom!"
        flash(msg)
        return redirect(url_for("show_main"))

    update_after_pledge_allegiance(db=db, player_name=player_name, noble_name=noble_name)
    return redirect(url_for("show_main"))


############################################################
################# Buy a Drink ########################
############################################################


@app.route("/buy_drink", methods=["POST"])
def buy_drink():
    """Process the request to buy a drink."""
    player_name = request.form["player_name"].strip().lower()
    drink_name = request.form["drink_name"]
    quantity = int(request.form["quantity"])

    db = get_db()

    noble_id = get_single_player(db=db, player_name=player_name, col="noble_id")
    if noble_id is None:
        msg = "Unsuccessful! You need to ally yourself to a noble before you can buy a drink."
        flash(msg)
        return redirect(url_for("show_main"))

    price = get_cost_for_a_drink(db=db, drink_name=drink_name)
    cost = price * quantity

    noble = get_single_player(db=db, player_id=noble_id)

    increment_coin(db=db, player_name=noble["player_name"], coin=-cost)
    increment_drinks(db=db, player_name=player_name, num=quantity)

    # the noble doesn't have any more money
    if noble["coin"] <= cost:
        new_noble_name = find_richest_peasant(db=db)
        upgrade_peasant_and_downgrade_noble(
            db=db, peasant_name=new_noble_name, noble_name=noble["player_name"]
        )
        msg = f"{noble['player_name']} ran out of money! {new_noble_name} is now a noble!"
        flash(msg)

    return redirect(url_for("show_main"))


############################################################
################# Ban a Peasant ########################
############################################################


@app.route("/ban", methods=["POST"])
def ban_peasant():
    """Respond to a request to ban a peasant from a noble's army."""
    noble_name = request.form["noble_name"].strip().lower()
    peasant_name = request.form["peasant_name"].strip().lower()

    db = get_db()
    noble = get_single_player(db=db, player_name=noble_name)

    if noble["player_status"] is None:
        msg = f"Unsuccessful! {noble_name} is not recognized. Did you enter your name correctly?"
        flash(msg)
        return redirect(url_for("show_main"))

    if noble["player_status"] != NOBLE:
        msg = f"Unsuccessful! {noble_name} is not a noble. You cannot ban people from kingdom you do not have."
        flash(msg)
        return redirect(url_for("show_main"))

    peasant = get_single_player(db=db, player_name=peasant_name)
    if peasant["id"] is None:
        msg = f"Unsuccessful! {peasant_name} is not recognized. Did you enter your name correctly?"
        flash(msg)
        return redirect(url_for("show_main"))

    # remove the peasant's allegiance to the noble that is banning them
    if peasant["noble_id"] == noble["id"]:
        set_allegiance(db=db, player_name=peasant_name, noble_id=None)
        increment_soldiers(db=db, player_name=noble_name, num=-1)

    # add the peasant to a banned table
    insert_new_outlaw(db=db, noble_id=noble["id"], peasant_id=peasant["id"])
    return redirect(url_for("show_main"))


############################################################
################# Get a Quest ########################
############################################################


@app.route("/get_quest", methods=["POST"])
@login_required
def get_quest():
    """Respond to a users request to get a quest."""
    player_name = request.form["player_name"].strip().lower()
    difficulty = request.form["difficulty"].strip().lower()

    db = get_db()
    party_id = current_user.id

    player = get_single_player(db=db, player_name=player_name)
    if player["id"] is None:
        msg = (
            f"Unsuccessful! {player_name} is not in the party. Did you enter your name correctly?"
        )
        flash(msg)
        redirect(url_for("show_main"))

    quest = get_random_quest(db=db, difficulty=difficulty)
    return render_template(
        "quest.html", player_name=player_name, difficulty=difficulty, quest=quest, party_id=party_id
    )


@app.route("/add_money", methods=["POST"])
def add_money():
    """Respond to a request after a user completes a quest."""
    player_name = request.form["player_name"].strip().lower()
    difficulty = request.form["difficulty"]
    result = request.form["result"]

    if result == "Yes":
        db = get_db()
        reward = get_reward_for_difficulty(db=db, difficulty=difficulty)
        increment_coin(db=db, player_name=player_name, coin=reward)

    return redirect(url_for("show_main"))


############################################################
################# Kill a Peasant ########################
############################################################


@app.route("/kill", methods=["POST"])
@login_required
def kill():
    """Respond to a request for a user to kill another user."""
    player_name = request.form["player_name"].strip().lower()
    target_name = request.form["target_name"].strip().lower()

    db = get_db()
    party_id = current_user.id

    player = get_single_player(db=db, player_name=player_name)
    target = get_single_player(db=db, player_name=target_name)

    if player["id"] is None:
        msg = f"Unsuccessful! {player_name} is not in the party."
        flash(msg)
        return redirect(url_for("show_main"))

    if target["id"] is None:
        msg = f"Unsuccessful! {target_name} is not in the party."
        flash(msg)
        return redirect(url_for("show_main"))

    if player["player_status"] == PEASANT and target["player_status"] == NOBLE:
        coin_needed = get_starting_coin_for_status(db=db, player_status=NOBLE)
        if player["coin"] < coin_needed:
            msg = f"Unsuccessful! You need {coin_needed} to assassinate a noble."
            flash(msg)
            return redirect(url_for("show_main"))

    challenge = get_random_challenge(db=db)

    return render_template(
        "kill.html",
        challenge=challenge,
        player_name=player_name,
        target_name=target_name,
        party_id=party_id,
    )


@app.route("/assassinate", methods=["POST"])
def assassinate():
    """Respond to request on if a user was assassinated."""
    player_name = request.form["player_name"]
    target_name = request.form["target_name"]
    winner_name = request.form["winner_name"]

    db = get_db()

    if player_name == winner_name:
        loser_name = target_name
    else:
        loser_name = player_name

    winner_status = get_single_players(db=db, player_name=winner_name, col="player_status")
    loser_status = get_single_players(db=db, player_id=loser_name, col="player_status")

    if winner_status == PEASANT and loser_status == NOBLE:
        upgrade_peasant_and_downgrade_noble(
            db=db, peasant_name=winner_name, noble_name=loser_name
        )
        msg = f"{winner_name} assassinated {loser_name}! {winner_name} is now a noble!"
    elif winner_status == NOBLE and loser_status == NOBLE:
        new_noble_name = find_richest_peasant(db=db)
        upgrade_peasant_and_downgrade_noble(
            db=db, peasant_name=new_noble_name, noble_name=loser_name
        )
        msg = f"{winner_name} assassinated {loser_name}! {new_noble_name} is now a noble!"
        flash(msg)
    else:
        move_coin_between_players(db=db, from_name=loser_name, to_name=winner_name)

    return redirect(url_for("show_main"))


############################################################
################# View the Database ########################
############################################################


@app.route("/kingdom")
@login_required
def show_kingdom():
    """Show the page that lists all players."""
    db = get_db()
    party_id = current_user.id

    players = get_all_players(db=db)
    return render_template("show_kingdom.html", players=players, party_id=party_id)


@app.route("/leaderboard")
@login_required
def show_leaderboard():
    """Show the page for the leaderboard."""
    db = get_db()
    party_id = current_user.id

    leaderboard = get_all_nobles(db=db)
    almighty_ruler = get_almighty_ruler(db=db)
    return render_template(
        "show_leaderboard.html",
        leaderboard=leaderboard,
        almighty_ruler=almighty_ruler,
        party_id=party_id,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0")
