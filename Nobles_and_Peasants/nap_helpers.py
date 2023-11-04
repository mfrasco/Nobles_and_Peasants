# functions that help exectute the main functions in nobles and peasants

from urllib.parse import urlparse, urljoin
from flask_login import current_user

def fetch_one(db, query_string, args):
    rv = db.execute(query_string, args).fetchone()
    if rv is None:
        return None
    else:
        return rv[0]


def get_starting_info(db, status, user_id):

    party_id = current_user.id

    query = f"select coin from starting_coin where party_id = '{party_id}' and status = ?"
    starting_coin = fetch_one(db, query, [status])
    if status == 'peasant':
        allegiance = None
        soldiers = 0
    else:
        allegiance = user_id
        soldiers = 1
    return starting_coin, allegiance, soldiers


def get_parties(db):
    query = 'select party_id from parties'
    parties = db.execute(query).fetchall()
    return parties


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc


def find_richest_peasant(db):

    party_id = current_user.id

    query = f"""
    select id
    from kingdom
    where party_id = '{party_id}' and status = ?
    order by coin desc, drinks desc
    limit 1
    """
    new_noble = fetch_one(db, query, ['peasant'])
    return new_noble


def decrement_previous_noble(db, new_noble):

    party_id = current_user.id
    
    query = f"""
    update kingdom
    set soldiers = soldiers - 1
    where party_id = '{party_id}' and id = (select allegiance from kingdom where party_id = '{party_id}' and id = ?)
    """
    db.execute(query, [new_noble])
    return None


def switch_allegiances(db, new_noble, old_noble):

    party_id = current_user.id

    # switch allegiance from old noble to new noble
    query = f"update kingdom set allegiance = ? where party_id = '{party_id}' and allegiance = ?"
    db.execute(query, [new_noble, old_noble])
    return None


def update_new_noble(db, new_noble):

    party_id = current_user.id

    # update status, allegiance, coin, soldiers for new noble
    query = f"select coin from starting_coin where party_id = '{party_id}' and status = ?"
    starting_coin = fetch_one(db, query, ['noble'])
    query = f"""
    update kingdom set status = ?
                       , allegiance = ?
                       , coin = (case when coin > ? then coin else ? end)
                       , soldiers = 1 + (
                            select count(*)
                            from kingdom
                            where party_id = '{party_id}' and allegiance = ? and id != ?
                         )
                      where party_id = '{party_id}' and id = ?
    """
    db.execute(query, ['noble', new_noble, starting_coin, starting_coin, new_noble, new_noble, new_noble])
    return None


def make_noble_peasant(db, old_noble):

    party_id = current_user.id


    # remove titles from old noble
    query = f"update kingdom set status = ?, soldiers = ? where party_id = '{party_id}' and id = ?"
    db.execute(query, ['peasant', 0, old_noble])

    # remove any entries in banned table for old noble
    query = f"delete from banned where party_id = '{party_id}' and noble = ?"
    db.execute(query, [old_noble])

    return None


def take_money(db, winner, loser):

    party_id = current_user.id
    
    query = f"select coin from kingdom where party_id = '{party_id}' and id = ?"
    loser_coin = fetch_one(db, query, [loser])

    if loser_coin > 0:
        query = f"update kingdom set coin = coin + ? where party_id = '{party_id}' and id = ?"
        db.execute(query, [loser_coin, winner])
        query = f"update kingdom set coin = 0 where party_id = '{party_id}' and id = ?"
        db.execute(query, [loser])

    return None


def n_beats_p(db, winner, loser):

    party_id = current_user.id

    take_money(db = db, winner = winner, loser = loser)

    # before chaning allegiances of loser, decrement soldiers for previous noble of loser
    decrement_previous_noble(db = db, new_noble = loser)

    # ally loser to winner and increment soldiers
    query = f"update kingdom set allegiance = ? where party_id = '{party_id}' and id = ?"
    db.execute(query, [winner, loser])
    query = f"update kingdom set soldiers = soldiers + 1 where party_id = '{party_id}' and id = ?"
    db.execute(query, [winner])

    return None


def p_beats_n(db, winner, loser):
    take_money(db = db, winner = winner, loser = loser)
    decrement_previous_noble(db = db, new_noble = winner)
    switch_allegiances(db = db, new_noble = winner, old_noble = loser)
    update_new_noble(db = db, new_noble = winner)
    make_noble_peasant(db = db, old_noble = loser)
    return None


def n_beats_n(db, winner, loser):

    party_id = current_user.id

    # give the money from the loser to the winner
    take_money(db = db, winner = winner, loser = loser)

    # give the soldiers from the loser to the winner
    switch_allegiances(db = db, new_noble = winner, old_noble = loser)
    query = f"""
    update kingdom
    set soldiers = (
        select count(*)
        from kingdom
        where party_id = '{party_id}' and allegiance = ?
    ) where party_id = '{party_id}' and id = ?
    """
    db.execute(query, [winner, winner])

    # find the next noble and make the loser a peasant
    new_noble = find_richest_peasant(db = db)
    make_noble_peasant(db = db, old_noble = loser)

    decrement_previous_noble(db = db, new_noble = new_noble)
    update_new_noble(db = db, new_noble = new_noble)
    return None

