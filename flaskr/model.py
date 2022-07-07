from flask_login import UserMixin
from . import db


class User(UserMixin, db.Model):
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    spotifyid = db.Column(db.String(1000))
    role = db.Column(db.String(20))


class Historique(db.Model):
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer)
    playlistsid = db.Column(db.String(5000))
    trackid = db.Column(db.String(100))
    prediction = db.Column(db.String(50))
    satisfaction = db.Column(db.Boolean)
    date = db.Column(db.DateTime)
