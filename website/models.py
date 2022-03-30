from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# class Credential(db.Model, UserMixin):
#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(150), unique=True)
#     password = db.Column(db.String(150))
#     first_name = db.Column(db.String(150))
#     address = db.Column(db.String(150))
#     cred = db.Column(db.Integer)

user_rent = db.Table('user_rent',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('movie_id', db.Integer, db.ForeignKey('movie.id'))
)

user_buy = db.Table('user_buy',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('movie_id', db.Integer, db.ForeignKey('movie.id'))
)

user_cart = db.Table('user_cart', 
    db.Column('user_cart', db.Integer, db.ForeignKey('user.id')),
    db.Column('movie_id', db.Integer, db.ForeignKey('movie.id'))
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    address = db.Column(db.String(150))
    cred = db.Column(db.Integer)
    movie_rent = db.relationship('Movie',secondary=user_rent, backref='user_who_rented')
    movie_buy = db.relationship('Movie',secondary=user_buy, backref='user_who_buy')
    movie_cart = db.relationship('Movie', secondary=user_cart, backref='user_who_cart')

    

class Staff(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    address = db.Column(db.String(150))
    cred = db.Column(db.Integer)

class Manager(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    address = db.Column(db.String(150))
    cred = db.Column(db.Integer)

class Movie(db.Model):
    id =  db.Column(db.Integer, primary_key=True)
    imdb_id = db.Column(db.String(150))
    rating = db.Column(db.Float)
    votes = db.Column(db.Integer)
    description = db.Column(db.String(2000))
    name = db.Column(db.String(150), nullable = False)
    genre = db.Column(db.String(150))
    rent_cost = db.Column(db.Integer, nullable = False)
    buy_cost = db.Column(db.Integer, nullable = False)
    quantity = db.Column(db.Integer)
    url = db.Column(db.String(200), nullable = False)
    in_data = db.Column(db.Integer)
    json_data = db.Column(db.JSON)
    poster = db.Column(db.LargeBinary)
     

