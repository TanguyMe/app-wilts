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
