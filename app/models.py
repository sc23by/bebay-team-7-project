from app import db
from flask_login import UserMixin
from sqlalchemy import ForeignKey

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

# Expert model
class ExpertAvailabilities(db.Model):
    availability_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)  # Each expert must be a unique user
    available = db.Column(db.Boolean)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    duration = db.Column(db.Integer)
    user = db.relationship('User', backref='expert_availabilities')


# Payment Info model
class PaymentInfo(db.Model):
    payment_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('user.id'), unique=True, nullable=False)  # One user should have one payment info
    payment_type = db.Column(db.String(30), nullable=False)
    shipping_address = db.Column(db.String(500), nullable=False)

# Sold item model
class Solditem(db.Model):
    sold_id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, ForeignKey('item.item_id'), nullable=False)
    seller_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    buyer_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)

# item model
class Item(db.Model):
    item_id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    item_name = db.Column(db.String(100), nullable=False)
    minimum_price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    item_image = db.Column(db.String(500), nullable=False)
    duration = db.Column(db.Time, nullable=False)
    time = db.Column(db.Time, nullable=False)
    date = db.Column(db.Date, nullable=False)
    approved = db.Column(db.Boolean, default=False)
    shipping_cost = db.Column(db.Float, nullable=False)

    # Store the fixed fees at the time of listing
    site_fee_percentage = db.Column(db.Float, nullable=False)
    expert_fee_percentage = db.Column(db.Float, nullable=False)

    def calculate_fee(self, final_price, expert_approved=False):
        if expert_approved:
            return final_price * ((self.site_fee_percentage + self.expert_fee_percentage) / 100)
        return final_price * (self.site_fee_percentage / 100)

# Bids model
class Bids(db.Model):
    bid_id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, ForeignKey('item.item_id'), nullable=False)
    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    bid_amount = db.Column(db.Float, nullable=False)  # Allows precise bid values
    bid_time = db.Column(db.Time, nullable=False)
    bid_date = db.Column(db.Date, nullable=False)

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

