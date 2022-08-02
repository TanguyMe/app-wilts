import pytest
import tempfile
from flaskr import create_app
from flask import Flask
import os

@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()
    os.environ['SQLALCHEMY_DATABASE_URI_SQLITE'] = "sqlite:///"+db_path
    os.environ['SQLALCHEMY_DATABASE_MSSQL'] = ''
    # create the app with common test config
    app = create_app({"TESTING": 'True'})

    yield app

    # close and remove the temporary database
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

# @pytest.fixture
# def client():
#     db_fd, db_path = tempfile.mkstemp()
#     os.environ['SQLALCHEMY_DATABASE_URI_SQLITE'] = "sqlite:///"+db_path
#     # create the app with common test config
#     app = create_app({"TESTING": 'True'})
#
#     yield app
#
#     # close and remove the temporary database
#     os.close(db_fd)
#     os.unlink(db_path)
    # app = create_app()
    # db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    # app.config['TESTING'] = True
    #
    # with app.test_client() as client:
    #     with app.app_context():
    #         import sqlalchemy
    #         engine = sqlalchemy.create_engine(os.environ("SQLALCHEMY_DATABASE_URI_TEST"))  # connect to server
    #         engine.execute("CREATE DATABASE wilts_app_test")  # create db
    #         engine.execute("USE wilts_app_test")  # select new db
    #         app.init_db()
    #     yield client
    #
    # os.close(db_fd)
    # os.unlink(app.config['DATABASE'])

    # app = create_app()
    # app.config['TESTING'] = True
    # with app.test_client() as client:
    #     yield client


# @pytest.fixture(scope='session')
# def database(request):
#     '''
#     Create a Postgres database for the tests, and drop it when the tests are done.
#     '''
#     import sqlalchemy
#     engine = sqlalchemy.create_engine(os.environ("SQLALCHEMY_DATABASE_URI_TEST"))  # connect to server
#     engine.execute("CREATE DATABASE wilts_app_test")  # create db
#     engine.execute("USE wilts_app_test")  # select new db
#     def drop_database():
#         engine.execute("DROP DATABASE wilts_app_test")
#     # pg_host = DB_OPTS.get("host")
#     # pg_port = DB_OPTS.get("port")
#     # pg_user = DB_OPTS.get("username")
#     # pg_db = DB_OPTS["database"]
#     #
#     # init_postgresql_database(pg_user, pg_host, pg_port, pg_db)
#     #
#     # @request.addfinalizer
#     # def drop_database():
#     #     drop_postgresql_database(pg_user, pg_host, pg_port, pg_db, 9.6)
#
#
# @pytest.fixture(scope='session')
# def app(database):
#     '''
#     Create a Flask app context for the tests.
#     '''
#     app = Flask(__name__)
#
#     app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI_TEST']
#
#     return app
#
#
# @pytest.fixture(scope='session')
# def _db(app):
#     '''
#     Provide the transactional fixtures with access to the database via a Flask-SQLAlchemy
#     database connection.
#     '''
#     db = SQLAlchemy(app=app)
#
#     return db