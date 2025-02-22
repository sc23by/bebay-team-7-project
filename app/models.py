from app import db
from flask_login import UserMixin
from sqlalchemy import ForeignKey

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    firstName = db.Column(db.String(30), nullable=False)
    lastName = db.Column(db.String(30), nullable=False)
    priority = db.Column(db.Integer, nullable=False, default=1)
    profilePicture = db.Column(db.String(255), nullable=False,default="default_profile.jpg")

# Expert model
class Expert(db.Model):
    ExpertId = db.Column(db.Integer, primary_key=True)
    UserId = db.Column(db.Integer, ForeignKey('user.id'), unique=True, nullable=False)  # Each expert must be a unique user
    Availability = db.Column(db.String(50), nullable=False)

# Payment Info model
class PaymentInfo(db.Model):
    PaymentId = db.Column(db.Integer, primary_key=True)
    UserId = db.Column(db.Integer, ForeignKey('user.id'), unique=True, nullable=False)  # One user should have one payment info
    PaymentType = db.Column(db.String(30), nullable=False)
    ShippingAddress = db.Column(db.String(500), nullable=False)

# Sold Items model
class SoldItems(db.Model):
    soldId = db.Column(db.Integer, primary_key=True)
    itemId = db.Column(db.Integer, ForeignKey('items.itemId'), nullable=False)
    sellerId = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    buyerId = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)

# Items model
class Items(db.Model):
    itemId = db.Column(db.Integer, primary_key=True)
    sellerId = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    itemName = db.Column(db.String(100), nullable=False)  # Removed unique constraint so same name can be reused
    minimumPrice = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    itemImage = db.Column(db.String(500), nullable=False)
    duration = db.Column(db.Time, nullable=False)
    time = db.Column(db.Time, nullable=False)
    date = db.Column(db.Date, nullable=False)
    approved = db.Column(db.Boolean, default=False)
    shippingCost = db.Column(db.Float, nullable=False)
    expertPaymentPercentage = db.Column(db.Float, nullable=False)

# Bids model
class Bids(db.Model):
    bidId = db.Column(db.Integer, primary_key=True)
    itemId = db.Column(db.Integer, ForeignKey('items.itemId'), nullable=False)
    userId = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    bidAmount = db.Column(db.Float, nullable=False)  # Allows precise bid values
    bidTime = db.Column(db.Time, nullable=False)
    bidDate = db.Column(db.Date, nullable=False)
