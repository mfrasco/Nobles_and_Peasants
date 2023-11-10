import os

from flask import Flask, render_template, session


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'nobles_and_peasants.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass


    @app.route("/")
    def show_login():
        """Show the login page."""
        party_name = session.get("party_name")
        return render_template("login.html", party_name=party_name)


    @app.route("/how_to_play")
    def how_to_play():
        """Show the how to play page."""
        party_name = session.get("party_name")
        return render_template("how_to_play.html", party_name=party_name)


    @app.route("/what_is_this")
    def what_is_this():
        """Show the what is this page."""
        party_name = session.get("party_name")
        return render_template("what_is_this.html", party_name=party_name)


    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import game
    app.register_blueprint(game.bp)
    # app.add_url_rule('/', endpoint='game')


    return app
