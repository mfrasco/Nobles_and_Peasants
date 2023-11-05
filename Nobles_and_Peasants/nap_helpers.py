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

    query = """
        select coin
        from starting_coin
        where party_id = ?
            and player_status = ?
    """
    starting_coin = fetch_one(db, query, [party_id, status])
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

    query = """
        select id
        from players
        where party_id = ?
            and player_status = ?
        order by coin desc, drinks desc
        limit 1
    """
    new_noble = fetch_one(db, query, [party_id, 'peasant'])
    return new_noble


def decrement_previous_noble(db, new_noble):

    party_id = current_user.id
    
    query = """
        update players
        set soldiers = soldiers - 1
        where party_id = ?
            and id = (select noble_id from players where party_id = ? and id = ?)
    """
    db.execute(query, [party_id, party_id, new_noble])
    return None


def switch_allegiances(db, new_noble, old_noble):

    party_id = current_user.id

    # switch allegiance from old noble to new noble
    query = """
        update players
        set noble_id = ?
        where party_id = ?
            and noble_id = ?
    """
    db.execute(query, [new_noble, party_id, old_noble])
    return None


def update_new_noble(db, new_noble):

    party_id = current_user.id

    # update status, allegiance, coin, soldiers for new noble
    query = """
        select coin
        from starting_coin
        where party_id = ?
            and player_status = ?
    """
    starting_coin = fetch_one(db, query, [party_id, 'noble'])
    query = """
    update players
    set player_status = ?
        , noble_id = ?
        , coin = (case when coin > ? then coin else ? end)
        , soldiers = 1 + (
            select count(*)
            from players
            where party_id = ?
                and noble_id = ?
                and id != ?
          )
    where party_id = ?
        and id = ?
    """
    db.execute(query, ['noble', new_noble, starting_coin, starting_coin, party_id, new_noble, new_noble, party_id, new_noble])
    return None


def make_noble_peasant(db, old_noble):

    party_id = current_user.id


    # remove titles from old noble
    query = """
        update players
        set player_status = ?
            , soldiers = ?
        where party_id = ?
            and id = ?
    """
    db.execute(query, ['peasant', 0, party_id, old_noble])

    # remove any entries in banned table for old noble
    query = """
        delete from outlaws
        where party_id = ?
            and noble_id = ?
    """
    db.execute(query, [party_id, old_noble])

    return None


def take_money(db, winner, loser):

    party_id = current_user.id
    
    query = """
        select coin
        from players
        where party_id = ?
            and id = ?
    """
    loser_coin = fetch_one(db, query, [party_id, loser])

    if loser_coin > 0:
        query = """
            update players
            set coin = coin + ?
            where party_id = ?
                and id = ?
        """
        db.execute(query, [loser_coin, party_id, winner])
        query = """
            update players
            set coin = 0
            where party_id = ?
                and id = ?
        """
        db.execute(query, [party_id, loser])

    return None


def n_beats_p(db, winner, loser):

    party_id = current_user.id

    take_money(db = db, winner = winner, loser = loser)

    # before chaning allegiances of loser, decrement soldiers for previous noble of loser
    decrement_previous_noble(db = db, new_noble = loser)

    # ally loser to winner and increment soldiers
    query = """
        update players
        set noble_id = ?
        where party_id = ?
            and id = ?
    """
    db.execute(query, [winner, party_id, loser])
    query = """
        update players
        set soldiers = soldiers + 1
        where party_id = ?
            and id = ?
    """
    db.execute(query, [party_id, winner])

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
    query = """
        update players
        set soldiers = (
            select count(*)
            from players
            where party_id = ?
                and noble_id = ?
        )
        where party_id = ?
            and id = ?
    """
    db.execute(query, [party_id, winner, party_id, winner])

    # find the next noble and make the loser a peasant
    new_noble = find_richest_peasant(db = db)
    make_noble_peasant(db = db, old_noble = loser)

    decrement_previous_noble(db = db, new_noble = new_noble)
    update_new_noble(db = db, new_noble = new_noble)
    return None

