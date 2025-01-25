from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    address = db.Column(db.String(750))
    password = db.Column(db.String(150))
    business_name = db.Column(db.String(150))
    username = db.Column(db.String(150), unique=True)
    registration_id = db.Column(db.String(500), unique=True)
    #notes = db.relationship('Note')