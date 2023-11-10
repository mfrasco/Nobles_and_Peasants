from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort

from nobles_and_peasants.auth import login_required
from nobles_and_peasants.challenges import get_random_challenge
from nobles_and_peasants.constants import NOBLE, PEASANT
from nobles_and_peasants.db import get_db
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
    does_party_name_exist,
    get_party_id,
    get_party_name,
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

bp = Blueprint('game', __name__)

@bp.route("/set_up", methods=["GET"])
@login_required
def set_up():
    """Show the setup page, where the player can customize the party settings."""
    db = get_db()

    drinks = get_drink_name_and_cost(db=db)
    starting_coin = get_status_and_starting_coin(db=db)
    quest_rewards = get_quest_difficulty_and_reward(db=db)

    return render_template(
        "setup.html",
        drinks=drinks,
        starting_coin=starting_coin,
        quest_rewards=quest_rewards,
        party_name=session.get("party_name"),
    )


@bp.route("/rules")
def show_rules():
    """Show the page that describes the rules."""
    return render_template("rules.html")


############################################################
################# Setup Party ########################
############################################################


@bp.route("/add_drink", methods=["POST"])
@login_required
def add_drink():
    """Process request to add a drink to the party."""
    db = get_db()
    drink_name = request.form["drink_name"].strip().lower()
    price = int(request.form["price"])

    add_or_update_drink_name_and_cost(db=db, drink_name=drink_name, drink_cost=price)
    return redirect(url_for("game.set_up"))


@bp.route("/set_coin", methods=["POST"])
@login_required
def set_coin():
    """Respond to request to set starting coin for each role."""
    db = get_db()
    noble_coin = int(request.form["noble_coin"])
    update_noble_starting_coin(db=db, noble_coin=noble_coin)
    return redirect(url_for("game.set_up"))


@bp.route("/set_wages", methods=["POST"])
@login_required
def set_wages():
    """Respond to a request to set rewards for quests."""
    easy_reward = int(request.form["easy"])
    medium_reward = int(request.form["medium"])
    hard_reward = int(request.form["hard"])

    if medium_reward < easy_reward:
        flash("Medium reward cannot be less than easy reward")
        return redirect(url_for("game.set_up"))

    if hard_reward < medium_reward:
        flash("Hard reward cannot be less than medium reward")
        return redirect(url_for("game.set_up"))

    db = get_db()
    set_quest_rewards(
        db=db,
        easy_reward=easy_reward,
        medium_reward=medium_reward,
        hard_reward=hard_reward,
    )

    return redirect(url_for("game.set_up"))

# ############################################################
# ################### Show main page #########################
# ############################################################

@bp.route("/main")
@login_required
def show_main():
    """Display the main page."""
    db = get_db()

    drinks = get_drink_name_and_cost(db=db)
    drink_names = [row["drink_name"] for row in drinks]

    players = get_all_players(db=db)
    player_names = [row["player_name"] for row in players]
    noble_names = [
        row["player_name"] for row in players if row["player_status"] == NOBLE
    ]

    return render_template(
        "main.html",
        drink_names=drink_names,
        player_names=player_names,
        noble_names=noble_names,
        party_name=session.get("party_name"),
    )

############################################################
################# Sign In ########################
############################################################


@bp.route("/sign_in", methods=["POST"])
@login_required
def sign_in():
    """Process a player's request to sign in to the game."""
    player_name = request.form["player_name"].strip().lower()
    player_status = request.form["player_status"]

    db = get_db()
    players = get_all_players(db=db)

    existing_players = [row["player_name"] for row in players]
    if player_name in existing_players:
        msg = f"Unsuccessful! Please choose a different name. Someone already selected {player_name}."
        flash(msg)
        return redirect(url_for("game.show_main"))

    if player_status == "randomly decide":
        status = randomly_choose_player_status(players=players)
    else:
        status = player_status

    insert_new_player(db=db, player_name=player_name, player_status=status)

    return redirect(url_for("game.show_main"))


############################################################
################# Pledge Allegiance ########################
############################################################


@bp.route("/pledge", methods=["POST"])
@login_required
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
        return redirect(url_for("game.show_main"))

    if noble["player_status"] is None:
        msg = f"Unsuccessful! Please enter a valid name for the noble. You entered: {noble_name}."
        flash(msg)
        return redirect(url_for("game.show_main"))

    if noble["player_status"] != NOBLE:
        msg = f"Unsuccessful! {noble_name} is not a noble."
        flash(msg)
        return redirect(url_for("game.show_main"))

    if player["player_status"] == NOBLE:
        msg = f"Unsuccessful! {player_name} is a noble. You must be allied to yourself."
        flash(msg)
        return redirect(url_for("game.show_main"))

    if is_peasant_banned(db=db, noble_id=noble["id"], peasant_id=player["id"]):
        msg = f"Unsuccessful! {noble_name} has banned you from their kingdom!"
        flash(msg)
        return redirect(url_for("game.show_main"))

    update_after_pledge_allegiance(
        db=db, player_name=player_name, noble_name=noble_name
    )
    return redirect(url_for("game.show_main"))


############################################################
################# Buy a Drink ########################
############################################################


@bp.route("/buy_drink", methods=["POST"])
@login_required
def buy_drink():
    """Process the request to buy a drink."""
    player_name = request.form["player_name"].strip().lower()
    drink_name = request.form["drink_name"]
    quantity = int(request.form["quantity"])

    db = get_db()

    noble_name = get_single_player(db=db, player_name=player_name, col="noble_name")
    if noble_name is None:
        msg = "Unsuccessful! You need to ally yourself to a noble before you can buy a drink."
        flash(msg)
        return redirect(url_for("game.show_main"))

    price = get_cost_for_a_drink(db=db, drink_name=drink_name)
    cost = price * quantity

    noble = get_single_player(db=db, player_name=noble_name)

    increment_coin(db=db, player_name=noble_name, coin=-cost)
    increment_drinks(db=db, player_name=player_name, num=quantity)

    # the noble doesn't have any more money
    if noble["coin"] <= cost:
        new_noble_name = find_richest_peasant(db=db)
        upgrade_peasant_and_downgrade_noble(
            db=db, peasant_name=new_noble_name, noble_name=noble_name
        )
        msg = f"{noble_name} ran out of money! {new_noble_name} is now a noble!"
        flash(msg)

    return redirect(url_for("game.show_main"))


############################################################
################# Ban a Peasant ########################
############################################################


@bp.route("/ban", methods=["POST"])
@login_required
def ban_peasant():
    """Respond to a request to ban a peasant from a noble's army."""
    noble_name = request.form["noble_name"].strip().lower()
    peasant_name = request.form["peasant_name"].strip().lower()

    db = get_db()
    noble = get_single_player(db=db, player_name=noble_name)

    if noble["player_status"] is None:
        msg = f"Unsuccessful! {noble_name} is not recognized. Did you enter your name correctly?"
        flash(msg)
        return redirect(url_for("game.show_main"))

    if noble["player_status"] != NOBLE:
        msg = f"Unsuccessful! {noble_name} is not a noble. You cannot ban people from kingdom you do not have."
        flash(msg)
        return redirect(url_for("game.show_main"))

    peasant = get_single_player(db=db, player_name=peasant_name)
    if peasant["id"] is None:
        msg = f"Unsuccessful! {peasant_name} is not recognized. Did you enter your name correctly?"
        flash(msg)
        return redirect(url_for("game.show_main"))

    # remove the peasant's allegiance to the noble that is banning them
    if peasant["noble_name"] == noble_name:
        set_allegiance(db=db, player_name=peasant_name, noble_name=None)
        increment_soldiers(db=db, player_name=noble_name, num=-1)

    # add the peasant to a banned table
    insert_new_outlaw(db=db, noble_id=noble["id"], peasant_id=peasant["id"])
    return redirect(url_for("game.show_main"))


############################################################
################# Get a Quest ########################
############################################################


@bp.route("/get_quest", methods=["POST"])
@login_required
def get_quest():
    """Respond to a player's request to get a quest."""
    player_name = request.form["player_name"].strip().lower()
    difficulty = request.form["difficulty"].strip().lower()

    db = get_db()

    player = get_single_player(db=db, player_name=player_name)
    if player["id"] is None:
        msg = f"Unsuccessful! {player_name} is not in the party. Did you enter your name correctly?"
        flash(msg)
        redirect(url_for("game.show_main"))

    quest = get_random_quest(db=db, difficulty=difficulty)
    return render_template(
        "quest.html",
        player_name=player_name,
        difficulty=difficulty,
        quest=quest,
        party_name=session.get("party_name"),
    )


@bp.route("/add_money", methods=["POST"])
@login_required
def add_money():
    """Respond to a request after a player completes a quest."""
    player_name = request.form["player_name"].strip().lower()
    difficulty = request.form["difficulty"]
    result = request.form["result"]

    if result == "Yes":
        db = get_db()
        reward = get_reward_for_difficulty(db=db, difficulty=difficulty)
        increment_coin(db=db, player_name=player_name, coin=reward)

    return redirect(url_for("game.show_main"))


############################################################
################# Kill a Peasant ########################
############################################################


@bp.route("/kill", methods=["POST"])
@login_required
def kill():
    """Respond to a request for a player to kill another player."""
    player_name = request.form["player_name"].strip().lower()
    target_name = request.form["target_name"].strip().lower()

    db = get_db()

    player = get_single_player(db=db, player_name=player_name)
    target = get_single_player(db=db, player_name=target_name)

    if player["id"] is None:
        msg = f"Unsuccessful! {player_name} is not in the party."
        flash(msg)
        return redirect(url_for("game.show_main"))

    if target["id"] is None:
        msg = f"Unsuccessful! {target_name} is not in the party."
        flash(msg)
        return redirect(url_for("game.show_main"))

    if player_name == target_name:
        msg = f"Unsuccessful! You cannot try to assassinate yourself!"
        flash(msg)
        return redirect(url_for("game.show_main"))

    if player["player_status"] == PEASANT and target["player_status"] == NOBLE:
        coin_needed = get_starting_coin_for_status(db=db, player_status=NOBLE)
        if player["coin"] < coin_needed:
            msg = f"Unsuccessful! You need {coin_needed} to assassinate a noble."
            flash(msg)
            return redirect(url_for("game.show_main"))

    challenge = get_random_challenge(db=db)

    return render_template(
        "kill.html",
        challenge=challenge,
        player_name=player_name,
        target_name=target_name,
        party_name=session.get("party_name"),
    )


@bp.route("/assassinate", methods=["POST"])
@login_required
def assassinate():
    """Respond to request on if a player was assassinated."""
    player_name = request.form["player_name"]
    target_name = request.form["target_name"]
    winner_name = request.form["winner_name"]

    db = get_db()

    if player_name == winner_name:
        loser_name = target_name
    else:
        loser_name = player_name

    winner_status = get_single_player(
        db=db, player_name=winner_name, col="player_status"
    )
    loser_status = get_single_player(db=db, player_name=loser_name, col="player_status")

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
        msg = (
            f"{winner_name} assassinated {loser_name}! {new_noble_name} is now a noble!"
        )
        flash(msg)
    else:
        move_coin_between_players(db=db, from_name=loser_name, to_name=winner_name)

    return redirect(url_for("game.show_main"))

# ############################################################
# ################# View the Database ########################
# ############################################################


@bp.route("/kingdom")
@login_required
def show_kingdom():
    """Show the page that lists all players."""
    db = get_db()
    players = get_all_players(db=db)
    return render_template(
        "show_kingdom.html", players=players, party_name=session.get("party_name")
    )


@bp.route("/leaderboard")
@login_required
def show_leaderboard():
    """Show the page for the leaderboard."""
    db = get_db()
    leaderboard = get_all_nobles(db=db)
    almighty_ruler = get_almighty_ruler(db=db)
    return render_template(
        "show_leaderboard.html",
        leaderboard=leaderboard,
        almighty_ruler=almighty_ruler,
        party_name=session.get("party_name"),
    )
