# functions that help exectute the main functions in nobles and peasants

def fetch_one(db, query_string, args):
    rv = db.execute(query_string, args).fetchone()
    if rv is None:
        return None
    else:
        return rv[0]


def get_starting_info(db, status, user_id):
    query = 'select coin from starting_coin where status = ?'
    starting_coin = fetch_one(db, query, [status])
    if status == 'peasant':
        allegiance = None
        soldiers = 0
    else:
        allegiance = user_id
        soldiers = 1
    return starting_coin, allegiance, soldiers


def find_richest_peasant(db):
    query = 'select id from kingdom where status = ? order by coin desc, drinks desc limit 1'
    new_noble = fetch_one(db, query, ['peasant'])
    return new_noble


def decrement_previous_noble(db, new_noble):
    query = '''
    update kingdom
    set soldiers = soldiers - 1
    where id = (select allegiance from kingdom where id = ?)
    '''
    db.execute(query, [new_noble])
    return None


def switch_allegiances(db, new_noble, old_noble):
    # switch allegiance from old noble to new noble
    query = 'update kingdom set allegiance = ? where allegiance = ?'
    db.execute(query, [new_noble, old_noble])
    return None


def update_new_noble(db, new_noble):
    # update status, allegiance, coin, soldiers for new noble
    query = 'select coin from starting_coin where status = ?'
    starting_coin = fetch_one(db, query, ['noble'])
    query = '''
    update kingdom set status = ?
                       , allegiance = ?
                       , coin = (case when coin > ? then coin else ? end)
                       , soldiers = 1 + (select count(*) from kingdom where allegiance = ? and id != ?)
                   where id = ?
    '''
    db.execute(query, ['noble', new_noble, starting_coin, starting_coin, new_noble, new_noble, new_noble])
    return None


def make_noble_peasant(db, old_noble):
    # remove titles from old noble
    query = 'update kingdom set status = ?, soldiers = ? where id = ?'
    db.execute(query, ['peasant', 0, old_noble])

    # remove any entries in banned table for old noble
    db.execute('delete from banned where noble = ?', [old_noble])

    return None


def take_money(db, winner, loser):
    query = 'select coin from kingdom where id = ?'
    loser_coin = fetch_one(db, query, [loser])

    if loser_coin > 0:
        query = 'update kingdom set coin = coin + ? where id = ?'
        db.execute(query, [loser_coin, winner])
        query = 'update kingdom set coin = 0 where id = ?'
        db.execute(query, [loser])

    return None


def n_beats_p(db, winner, loser):
    take_money(db = db, winner = winner, loser = loser)

    # before chaning allegiances of loser, decrement soldiers for previous noble of loser
    decrement_previous_noble(db = db, new_noble = loser)

    # ally loser to winner and increment soldiers
    db.execute('update kingdom set allegiance = ? where id = ?', [winner, loser])
    db.execute('update kingdom set soldiers = soldiers + 1 where id = ?', [winner])

    return None


def p_beats_n(db, winner, loser):
    take_money(db = db, winner = winner, loser = loser)
    decrement_previous_noble(db = db, new_noble = winner)
    switch_allegiances(db = db, new_noble = winner, old_noble = loser)
    update_new_noble(db = db, new_noble = winner)
    make_noble_peasant(db = db, old_noble = loser)
    return None


def n_beats_n(db, winner, loser):
    # give the money from the loser to the winner
    take_money(db = db, winner = winner, loser = loser)

    # give the soldiers from the loser to the winner
    switch_allegiances(db = db, new_noble = winner, old_noble = loser)
    query = '''
    update kingdom set soldiers = (
        select count(*) from kingdom where allegiance = ?
    ) where id = ?
    '''
    db.execute(query, [winner, winner])

    # find the next noble and make the loser a peasant
    new_noble = find_richest_peasant(db = db)
    make_noble_peasant(db = db, old_noble = loser)

    decrement_previous_noble(db = db, new_noble = new_noble)
    update_new_noble(db = db, new_noble = new_noble)
    return None

