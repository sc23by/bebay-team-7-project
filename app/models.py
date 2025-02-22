from app import db
from flask_login import UserMixin
from sqlalchemy.sql import func

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)


# jays code
from . import db

class User(db.Model):
    id = db.Colmn(db.Integer, primary_key = True)
    firstName = db.Column(db.String(30),nullable=False)
    lastName = db.Column(db.String(30),nullable=False)
    username = db.Column(db.String(100),nullable=False,unique=True)
    email = db.Column(db.String(100),nullable=False,unique=True)
    priority = db.Column(db.Integer,nullable=False)
    profilePicture = db.Column(db.String(50),nullable=False)

class Expert(db.Model):
    ExpertId = db.Column(db.Integer, primary_key = True)
    UserId = db.Column(db.Integer, ForeignKey('User.id'))
    Availability = db.Column(db.String(50),nullable=False)

class PaymentInfo(db.Model):
    PaymentId = db.Column(db.Integer, primary_key = True)
    UserId = db.Column(db.Integer, ForeignKey('user.id'))
    PaymentType = db.Column(db.String(30),nullable=False)
    ShippingAddress = db.Column(db.String(500),nullable=False)

class SoldItems(db.Model):
    soldId = db.Column(db.Integer, primary_key = True)
    itemId = db.Column(db.Integer,ForeignKey('Item.itemId'))
    sellerId = db.Column(db.Integer,ForeignKey('Item.id'))
    buyerId = db.Column(db.Integer,ForeignKey('User.id'))
    price = db.Column(db.Float)

class Items(db.Model):
    itemId = db.Column(db.Integer)
    sellerId = db.Column(db.Integer)
    itemName = db.Column(db.String(100))
    minimumPrice = db.Column(db.Float)
    description = db.Column(db.String(500))
    itemImage = db.Column(db.String(500))
    duration = db.Column(db.Time)
    time = db.Column(db.Time)
    date = db.Column(db.Date)
    approved = db.Column(db.Boolean)
    shippingCost = db.Column(db.Float)
    expertPaymentPercentageFloat = db.Column(db.Float)

class Bids(db.Model):
    bidId = db.Column(db.Integer)
    itemId = db.Column(db.Integer)
    userId = db.Column(db.Integer)
    bidAmount = db.Column(db.Integer)
    bidTime = db.Column(db.Time)
    bidDate = db.Column(db.Date)