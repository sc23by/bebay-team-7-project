
from app import db
from flask import url_for
from flask_login import UserMixin
from sqlalchemy import ForeignKey
from datetime import datetime, timedelta

# Association model between watched item and user
Watched_item = db.Table(
    'watched_item',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('item_id', db.Integer, db.ForeignKey('item.item_id'), primary_key=True)
)

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    priority = db.Column(db.Integer, nullable=False, default=1)
    profile_picture = db.Column(db.String(255), nullable=False, default="default_profile.jpg")

    watchlist = db.relationship('Item', secondary=Watched_item, backref='watched_by') # allows user to watch multiple items
    items = db.relationship('Item',foreign_keys='Item.seller_id',backref='seller',lazy=True)

# Expert model
class ExpertAvailabilities(db.Model):
    availability_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)  # Each expert must be a unique user
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    duration = db.Column(db.Integer, default=1)
    user = db.relationship('User', backref='expert_availabilities')


# Payment Info model
class PaymentInfo(db.Model):
    payment_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('user.id'), unique=True, nullable=False)  # One user should have one payment info
    payment_type = db.Column(db.String(30), nullable=True)
    shipping_address = db.Column(db.String(500), nullable=True)

# Sold item model
class Solditem(db.Model):
    sold_id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, ForeignKey('item.item_id'), nullable=False)
    seller_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    buyer_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)

# Item model
class Item(db.Model):
    item_id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    item_name = db.Column(db.String(100), nullable=False)
    minimum_price = db.Column(db.Numeric(10,2), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    item_image = db.Column(db.String(500), nullable=False)
    date_time = db.Column(db.DateTime, nullable=True)
    days = db.Column(db.Integer, nullable=False, default=0)
    hours = db.Column(db.Integer, nullable=False, default=0)
    minutes = db.Column(db.Integer, nullable=False, default=0)
    expiration_time = db.Column(db.DateTime, nullable=True)  
    approved = db.Column(db.Boolean, default=False)
    shipping_cost = db.Column(db.Numeric(10,2), nullable=False)
    expert_payment_percentage = db.Column(db.Float, nullable=False, default=0.00) # Default can be changed by managers
    expert_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = True)
    # Store the fixed fees at the time of listing
    site_fee_percentage = db.Column(db.Float, nullable=False,default=0.00)
    expert_fee_percentage = db.Column(db.Float, nullable=False,default=0.00)
    
    def get_image_url(self):
        return url_for('static', filename=f'images/items/{self.item_image}')

    @property
    def time_left(self):
        """Calculate remaining time from now until expiration."""
        if self.expiration_time is None:
            return timedelta(0)  # Return zero time if expiration_time is None
        remaining = self.expiration_time - datetime.utcnow()
        return max(remaining, timedelta(0))  # Ensure it doesn't go negative

    def calculate_fee(self, final_price, expert_approved=False):
        if expert_approved:
            return final_price * ((self.site_fee_percentage + self.expert_fee_percentage) / 100)
        return final_price * (self.site_fee_percentage / 100)
# Establish a relationship with User model (expert)
    expert = db.relationship('User', foreign_keys=[expert_id], backref='assigned_items')


# Waiting List Model
class WaitingList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.item_id'), nullable=False, unique=True)  # Ensures an item isn't requested twice
    request_time = db.Column(db.DateTime, default=datetime.utcnow)
    expire_time = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(days=2))

# Bid model
class Bid(db.Model):
    bid_id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, ForeignKey('item.item_id'), nullable=False)
    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    bid_amount = db.Column(db.Numeric(10, 2), nullable=False)  # Allows precise bid values
    bid_date_time = db.Column(db.DateTime, nullable=False)

# Fee Configuration Model (New)
class FeeConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    site_fee_percentage = db.Column(db.Float, nullable=False, default=1.0)  # Default 1%
    expert_fee_percentage = db.Column(db.Float, nullable=False, default=4.0)  # Default 4%

    @staticmethod
    def get_current_fees():
        fee = FeeConfig.query.first()
        if not fee:
            fee = FeeConfig(site_fee_percentage=1.0, expert_fee_percentage=4.0)
            db.session.add(fee)
            db.session.commit()
        return fee

