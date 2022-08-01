
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.security import generate_password_hash
import urllib.parse

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()

def create_app(config={}):
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
    if os.environ['SQLALCHEMY_DATABASE_MSSQL']:
        params = urllib.parse.quote_plus(os.environ['SQLALCHEMY_DATABASE_MSSQL'])
        app.config['SQLALCHEMY_DATABASE_URI'] = "mssql+pyodbc:///?odbc_connect=%s" % params
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI_SQLITE']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.environ['SQLALCHEMY_TRACK_MODIFICATIONS']
    for key, value in config.items():
        app.config[key] = value

    from .model import User, Historique
    db.init_app(app)
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(email=os.environ["ADMIN_MAIL"]).first():
            # create new user with the form data. Hash the password so plaintext version isn't saved.
            admin_user = User(email=os.environ["ADMIN_MAIL"], spotifyid=os.environ["ADMIN_SPOTIFYID"], password=generate_password_hash(os.environ["ADMIN_PASSWORD"], method='sha256'), role="admin")
            # add the new user to the database
            db.session.add(admin_user)
            db.session.commit()

    login_manager = LoginManager()
    login_manager.login_view = 'main.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    # blueprint for non-auth parts of app
    from .views import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
# import os
# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from flask_login import LoginManager
#
# app = Flask(__name__)
# app.config.from_object('config')
#
# # Create database connection object
# db = SQLAlchemy(app)
# #db.init_app(app)
#
# login_manager = LoginManager()
# login_manager.login_view = 'login'
# login_manager.init_app(app)
#
# from flaskr import model, views
#
#
# @login_manager.user_loader
# def load_user(user_id):
#     # since the user_id is just the primary key of our user table, use it in the query for the user
#     return model.User.query.get(int(user_id))
#
#
# @app.cli.command("init_db")
# def init_db():
#     model.init_db()

