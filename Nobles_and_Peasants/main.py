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

from Nobles_and_Peasants.challenges import get_random_challenge
from Nobles_and_Peasants.drinks import (
    add_or_update_drink_name_and_cost,
    get_cost_for_a_drink,
    get_drink_name_and_cost,
)
from Nobles_and_Peasants.outlaws import (
    is_peasant_banned,
    insert_new_outlaw,
)
from Nobles_and_Peasants.parties import (
    does_party_id_exist,
    get_hashed_password,
    insert_new_party,
)
from Nobles_and_Peasants.players import (
    find_richest_peasant,
    get_all_nobles,
    get_all_player_info,
    get_almighty_ruler,
    get_single_player_info,
    increment_coin_for_user,
    increment_drinks_for_user,
    increment_soldiers_for_user,
    insert_new_player,
    move_coin_from_user_to_user,
    randomly_choose_player_status,
    update_info_after_pledge_allegiance,
    upgrade_peasant_and_downgrade_noble,
    set_allegiance_for_user,
)
from Nobles_and_Peasants.starting_coin import (
    get_status_and_starting_coin,
    get_starting_coin_for_status,
    update_noble_starting_coin,
)
from Nobles_and_Peasants.quests import get_random_quest
from Nobles_and_Peasants.quest_rewards import (
    get_quest_difficulty_and_reward,
    get_reward_for_difficulty,
    set_quest_rewards,
)


# create the application instance and load config
app = Flask(__name__)
app.secret_key = "super secret key"

# app = Flask(__name__, instance_relative_config=True)
# app.config.from_object('Nobles_and_Peasants.default_settings')
# app.config.from_pyfile('application.cfg', silent=True)

############################################################
################# Setup Database ########################
############################################################


def connect_db():
    """Connects to the specific database."""
    # rv = sqlite3.connect(app.config['DATABASE'])
    rv = sqlite3.connect("Nobles_and_Peasants/flask_test.db")
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

    players = get_all_player_info(db=db)
    player_names = [row["id"] for row in players]
    noble_names = [row["id"] for row in players if row["player_status"] == "noble"]

    return render_template(
        "main.html",
        drinks=drink_names,
        people=player_names,
        nobles=noble_names,
        party_id=party_id,
    )


############################################################
################# Sign In ########################
############################################################


@app.route("/sign_in", methods=["POST"])
def sign_in():
    """Process a users request to sign in to the game."""
    user_id = request.form["user_id"].strip().lower()
    user_status = request.form["user_status"]

    db = get_db()
    players = get_all_player_info(db=db)

    existing_players = [row["id"] for row in players]
    if user_id in existing_players:
        msg = f"Unsuccessful! Please choose a different id. Someone already selected {user_id}."
        flash(msg)
        return redirect(url_for("show_main"))

    if user_status == "randomly decide":
        player_status = randomly_choose_player_status(players=players)
    else:
        player_status = user_status

    insert_new_player(db=db, user_id=user_id, player_status=player_status)

    return redirect(url_for("show_main"))


############################################################
################# Pledge Allegiance ########################
############################################################


@app.route("/pledge", methods=["POST"])
def pledge_allegiance():
    """Process the request to pledge allegiance to a noble."""
    user_id = request.form["user_id"].strip().lower()
    noble_id = request.form["noble_id"].strip().lower()

    db = get_db()
    user = get_single_player_info(db=db, user_id=user_id)
    noble = get_single_player_info(db=db, user_id=noble_id)

    if user["player_status"] is None:
        msg = f"Unsuccessful! Please enter a valid id for yourself. You entered: {user_id}. Have you signed in?"
        flash(msg)
        return redirect(url_for("show_main"))

    if noble["player_status"] is None:
        msg = f"Unsuccessful! Please enter a valid id for the noble. You entered: {noble_id}."
        flash(msg)
        return redirect(url_for("show_main"))

    if noble["player_status"] != "noble":
        msg = f"Unsuccessful! {noble_id} is not a noble."
        flash(msg)
        return redirect(url_for("show_main"))

    if user["player_status"] == "noble":
        msg = f"Unsuccessful! {user_id} is a noble. You must be allied to yourself."
        flash(msg)
        return redirect(url_for("show_main"))

    if is_peasant_banned(db=db, noble_id=noble_id, peasant_id=user_id):
        msg = f"Unsuccessful! {noble_id} has banned you from their kingdom!"
        flash(msg)
        return redirect(url_for("show_main"))

    update_info_after_pledge_allegiance(db=db, user_id=user_id, noble_id=noble_id)
    return redirect(url_for("show_main"))


############################################################
################# Buy a Drink ########################
############################################################


@app.route("/buy_drink", methods=["POST"])
def buy_drink():
    """Process the request to buy a drink."""
    user_id = request.form["user_id"].strip().lower()
    drink_name = request.form["drink"]
    quantity = int(request.form["quantity"])

    db = get_db()

    noble_id = get_single_player_info(db=db, user_id=user_id)["noble_id"]
    if noble_id is None:
        msg = "Unsuccessful! You need to ally yourself to a noble before you can buy a drink."
        flash(msg)
        return redirect(url_for("show_main"))

    price = get_cost_for_a_drink(db=db, drink_name=drink_name)
    cost = price * quantity

    noble_coin = get_single_player_info(db=db, user_id=noble_id)["coin"]

    increment_coin_for_user(db=db, user_id=noble_id, coin=-cost)
    increment_drinks_for_user(db=db, user_id=user_id, num=quantity)

    # the noble doesn't have any more money
    if noble_coin <= cost:
        new_noble_id = find_richest_peasant(db=db)
        upgrade_peasant_and_downgrade_noble(
            db=db, peasant_id=new_noble_id, noble_id=noble_id
        )
        msg = f"{noble_id} ran out of money! {new_noble_id} is now a noble!"
        flash(msg)

    return redirect(url_for("show_main"))


############################################################
################# Ban a Peasant ########################
############################################################


@app.route("/ban", methods=["POST"])
def ban_peasant():
    """Respond to a request to ban a peasant from a noble's army."""
    noble_id = request.form["noble_id"].strip().lower()
    peasant_id = request.form["peasant_id"].strip().lower()

    db = get_db()
    noble = get_single_player_info(db=db, user_id=noble_id)

    if noble["player_status"] is None:
        flash(
            f"Unsuccessful! ID: {noble_id} is not recognized. Did you enter your ID correctly?"
        )
        return redirect(url_for("show_main"))

    if noble["player_status"] != "noble":
        msg = f"Unsuccessful! {noble_id} is not a noble. You cannot ban people from kingdom you do not have."
        flash(msg)
        return redirect(url_for("show_main"))

    peasant = get_single_player_info(db=db, user_id=peasant_id)
    if peasant["id"] is None:
        msg = f"Unsuccessful! {peasant_id} does not exist. Did you enter it correctly?"
        flash(msg)
        return redirect(url_for("show_main"))

    # remove the peasant's allegiance to the noble that is banning them
    if peasant["noble_id"] == noble_id:
        set_allegiance_for_user(db=db, user_id=peasant_id, noble_id=None)
        increment_soldiers_for_user(db=db, user_id=noble_id, num=-1)

    # add the peasant to a banned table
    insert_new_outlaw(db=db, noble_id=noble_id, peasant_id=peasant_id)
    return redirect(url_for("show_main"))


############################################################
################# Get a Quest ########################
############################################################


@app.route("/get_quest", methods=["POST"])
@login_required
def get_quest():
    """Respond to a users request to get a quest."""
    user_id = request.form["user_id"].strip().lower()
    difficulty = request.form["level"].strip().lower()

    db = get_db()
    party_id = current_user.id

    user = get_single_player_info(db=db, user_id=user_id)
    if user["id"] is None:
        msg = (
            f"Unsuccessful! {user_id} is not in the party. Did you enter it correctly?"
        )
        flash(msg)
        redirect(url_for("show_main"))

    quest = get_random_quest(db=db, difficulty=difficulty)
    return render_template(
        "quest.html", id=user_id, level=difficulty, quest=quest, party_id=party_id
    )


@app.route("/add_money", methods=["POST"])
def add_money():
    """Respond to a request after a user completes a quest."""
    user_id = request.form["user_id"].strip().lower()
    difficulty = request.form["level"]
    result = request.form["result"]

    if result == "Yes":
        db = get_db()
        reward = get_reward_for_difficulty(db=db, difficulty=difficulty)
        increment_coin_for_user(db=db, user_id=user_id, coin=reward)

    return redirect(url_for("show_main"))


############################################################
################# Kill a Peasant ########################
############################################################


@app.route("/kill", methods=["POST"])
@login_required
def kill():
    """Respond to a request for a user to kill another user."""
    user_id = request.form["user_id"].strip().lower()
    target_id = request.form["target_id"].strip().lower()

    db = get_db()
    party_id = current_user.id

    user = get_single_player_info(db=db, user_id=user_id)
    target = get_single_player_info(db=db, user_id=target_id)

    if user["id"] is None:
        msg = (
            f"Unsuccessful! {user_id} is not in the party. Did you enter it correctly?"
        )
        flash(msg)
        return redirect(url_for("show_main"))

    if target["id"] is None:
        msg = f"Unsuccessful! {target_id} is not in the party. Did you enter it correctly?"
        return redirect(url_for("show_main"))

    if user["player_status"] == "peasant" and target["player_status"] == "noble":
        coin_needed = get_starting_coin_for_status(db=db, player_status="noble")
        if user["coin"] < coin_needed:
            msg = f"Unsuccessful! You need {coin_needed} to assassinate a noble."
            flash(msg)
            return redirect(url_for("show_main"))

    challenge = get_random_challenge(db=db)

    return render_template(
        "kill.html",
        challenge=challenge,
        user_id=user_id,
        target_id=target_id,
        party_id=party_id,
    )


@app.route("/assassinate", methods=["POST"])
def assassinate():
    """Respond to request on if a user was assassinated."""
    user_id = request.form["user_id"]
    target_id = request.form["target_id"]
    winner_id = request.form["winner"]

    db = get_db()

    if user_id == winner_id:
        loser_id = target_id
    else:
        loser_id = user_id

    winner = get_single_player_info(db=db, user_id=winner_id)
    loser = get_single_player_info(db=db, user_id=loser_id)

    if winner["player_status"] == "peasant" and loser["player_status"] == "noble":
        upgrade_peasant_and_downgrade_noble(
            db=db, peasant_id=winner_id, noble_id=loser_id
        )
        msg = f"{winner_id} assassinated {loser_id}! {winner_id} is now a noble!"
    elif winner["player_status"] == "noble" and loser["player_status"] == "noble":
        new_noble_id = find_richest_peasant(db=db)
        upgrade_peasant_and_downgrade_noble(
            db=db, peasant_id=new_noble_id, noble_id=loser_id
        )
        msg = f"{winner_id} assassinated {loser_id}! {new_noble_id} is now a noble!"
        flash(msg)
    else:
        move_coin_from_user_to_user(db=db, from_id=loser_id, to_id=winner_id)

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

    kingdom = get_all_player_info(db=db)
    return render_template("show_kingdom.html", kingdom=kingdom, party_id=party_id)


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
