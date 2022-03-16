import os

basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'mysql:///' + os.path.join(basedir, 'app.db')
SECRET_KEY = 'dont_tell_anyone'
SQLALCHEMY_TRACK_MODIFICATIONS = False