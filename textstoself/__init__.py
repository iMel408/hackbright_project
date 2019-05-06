import os
from flask import Flask


def create_app(test_config=None):

    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        # a default secret that should be overridden by instance config
        SECRET_KEY='dev'
    ),

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.update(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/')
    def hello():

        return 'Flask is Live!'

    from textstoself.model import connect_to_db, db
    connect_to_db(app)
    db.init_app(app)

    from textstoself import auth, application
    app.register_blueprint(auth.bp)
    app.register_blueprint(application.bp)
    app.add_url_rule('/', endpoint='user')

    return app
