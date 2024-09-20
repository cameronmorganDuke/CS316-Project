from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

#Can change this to properties interested in eventually
class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True) #software is smart enough to always advance id's
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())  #func gets the current data and time and stores is as the default value
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) #like a weak entity set



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True) #simular to SQL
    email = db.Column(db.String(150), unique=True) #simular to SQL
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    notes = db.relationship('Note') #list of all the different not id's