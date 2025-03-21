from app import app, db, bcrypt
from flask import render_template, redirect, url_for, request, flash, current_app, jsonify
from flask_login import login_user, current_user, login_required,logout_user
from app.forms import RegistrationForm, LoginForm, SideBarForm, UserInfoForm, ChangeUsernameForm, ChangeEmailForm, ChangePasswordForm, CardInfoForm, ListItemForm, BidForm, EditExpertiseForm, CATEGORY_CHOICES 
from app.models import User, Item, Bid, WaitingList, ExpertAvailabilities, Watched_item, PaymentInfo, Notification, SoldItem, UserMessage, FeeConfig
from functools import wraps
import matplotlib
matplotlib.use("Agg")  # Use a non-GUI backend
import matplotlib.pyplot as plt
import io
import base64
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime, timedelta
from sqlalchemy import desc
import numpy as np
import stripe
from datetime import datetime
# Parses data sent by JS
import json
# Websockets
from flask_socketio import emit
from . import socketio
# Emails
from flask_mail import Message
from app import mail
# Decorators

# Guest-only access decorator
def guest_required(f):
    """
    Decorator to restrict access to guests (not logged-in users) only.
    Redirects authenticated users to the appropriate dashboard.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            flash('You are already logged in.', 'info')
            # Redirect based on user priority
            return redirect_based_on_priority(current_user)
        return f(*args, **kwargs)
    return decorated_function

# User-only access decorator
def user_required(f):
    """
    Decorator to restrict access to authenticated users only.
    If the user is not logged in, they are redirected to the login page.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please log in first.", "warning")
            return redirect(url_for('login'))
        # If not a user
        if current_user.priority != 1:
            flash("You don't have user permissions to access this page.", "danger")
            return redirect_based_on_priority(current_user)
        return f(*args, **kwargs)
    return decorated_function

# Expert-only access decorator
def expert_required(f):
    """
    Decorator to restrict access to experts only (priority = 2).
    If the user is not an expert, they are redirected to their appropriate home page.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please log in first.", "warning")
            return redirect(url_for('login'))
        # If not an expert
        if current_user.priority != 2:
            flash("You don't have expert permissions to access this page.", "danger")
            return redirect_based_on_priority(current_user)
        return f(*args, **kwargs)
    return decorated_function

# Manager-only access decorator
def manager_required(f):
    """
    Decorator to restrict access to managers only (priority = 3).
    If the user is not a manager, they are redirected to their appropriate home page.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please log in first.", "warning")
            return redirect(url_for('login'))
        # If not a manager
        if current_user.priority != 3:
            flash("You don't have manager permissions to access this page.", "danger")
            return redirect_based_on_priority(current_user)
        return f(*args, **kwargs)
    return decorated_function


# Functions

# Function: Redirect based on priority
def redirect_based_on_priority(user):
    """
    Function to redirect user to correct page based on their priority.
    """
    if user.priority == 3:  # Manager
        return redirect(url_for('manager_home'))
    elif user.priority == 2:  # Expert
        return redirect(url_for('expert_assignments'))
    elif user.priority == 1:  # Normal User
        return redirect(url_for('user_home'))
    else:  # Guest
        return redirect(url_for('guest_home'))

# Function: Allow only certain filename endings for images
def allowed_file(filename):
    if not filename or '.' not in filename:
        return False  # Ensure empty or invalid filenames fail early
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in app.config['ALLOWED_EXTENSIONS']

# Function: Expired Auctions
def check_expired_auctions():
    """Check for expired auctions and send notifications."""
    with current_app.app_context():
        expired_items = Item.query.filter(Item.expiration_time <= datetime.utcnow(), Item.sold == False).all()
        #print("EXPIRED CHECK")
        for item in expired_items:
            highest_bid = item.highest_bid()
            highest_bidder = item.highest_bidder()

            # Notify highest bidder if they exist
            if highest_bidder:
                win_notification = Notification(
                    user_id=highest_bidder.id,
                    message=f"Congratulations! You have won the auction for '{item.item_name}' with a bid of £{highest_bid:.2f}."
                )
                db.session.add(win_notification)
                # Send email notification to the winner
                send_winner_email(highest_bidder, item, highest_bid)

            # Notify all previous bidders (updated: using item.item_id instead of item.id)
            previous_bidders = db.session.query(Bid.user_id).filter(Bid.item_id == item.item_id).distinct().all()
            for bidder in previous_bidders:
                if highest_bidder and bidder[0] == highest_bidder.id:
                    continue
                notification = Notification(
                    user_id=bidder[0],
                    message=f"The auction for '{item.item_name}' has ended."
                )
                db.session.add(notification)

            # Notify the seller
            if highest_bidder:
                seller_notification = Notification(
                    user_id=item.seller_id,
                    message=f"Your item '{item.item_name}' has been sold to {highest_bidder.username} for £{highest_bid:.2f}."
                )

                sold_item = SoldItem(
                    item_id=item.item_id,
                    seller_id=item.seller_id,
                    buyer_id=highest_bidder.id,
                    price=float(highest_bid)
                )
                db.session.add(sold_item)
            else:
                seller_notification = Notification(
                    user_id=item.seller_id,
                    message=f"Your item '{item.item_name}' has expired with no bids."
                )
            db.session.add(seller_notification)

            # Mark item as sold
            item.sold = True

            db.session.commit()

            # Broadcast auction end event (updated: using item.item_id)
            socketio.emit('auction_ended', {'item_id': item.item_id, 'winner_id': highest_bidder.id if highest_bidder else None})

def send_winner_email(winner, item, highest_bid):
    subject = f"You have won the auction for {item.item_name}!"
    recipients = [winner.email]
    body = f"""
Hi {winner.username},

Congratulations! You have won the auction for '{item.item_name}' with a bid of £{highest_bid:.2f}.

Thank you for participating in Bebay auctions!

Best regards,
The Bebay Team
"""
    msg = Message(subject=subject, recipients=recipients, body=body)
    mail.send(msg)

# Guest Pages

@app.route('/')
@guest_required
def guest_home():
    """
    Redirects to main page when website first opened.
    """
    if current_user.is_authenticated:
        return redirect_based_on_priority(current_user)
    return render_template('guest_home.html')


# Route: Registration Page    
@app.route('/register', methods=['GET', 'POST'])
@guest_required
def register():
    """
    Handle user registration.
    """
    form = RegistrationForm()

    if current_user.is_authenticated:
        return redirect_based_on_priority(current_user)

    if form.validate_on_submit():

        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('register'))

        if User.query.filter_by(email=form.email.data).first():
            flash('Email already exists. Please choose a different one.', 'danger')
            return redirect(url_for('register'))

        hashed_password = bcrypt.generate_password_hash(form.password.data)
        user = User(first_name=form.first_name.data, last_name=form.last_name.data, username=form.username.data, email=form.email.data, password=hashed_password)

        db.session.add(user)
        db.session.commit()

        # set up user ID in payment info table so that info can be updated later 
        payment_info = PaymentInfo(user_id=user.id)

        db.session.add(payment_info)
        db.session.commit()
        
        return redirect(url_for('login'))
    elif form.errors:
        flash('There were errors in the form. Please correct them.', 'danger')
    return render_template('register.html', form=form)

# Route: Login Page
@app.route('/login', methods=['GET', 'POST'])
@guest_required
def login():
    """
    Handle user login. Redirect to dashboard if already logged in.
    """
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect_based_on_priority(current_user)
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect_based_on_priority(current_user)
        flash('Invalid username or password.', 'danger')
    return render_template('login.html', form=form)


# All logged in pages

# Route: Logout
@app.route('/logout')
@login_required
def logout():
    """
    Log the user out and redirect to the guest_home page.
    """
    logout_user()
    return redirect(url_for('guest_home'))

@app.route('/messages')
@login_required
def messages():
    # Fetch conversation history using the renamed model
    messages = UserMessage.query.filter(
        ((UserMessage.sender_id == current_user.id) | (UserMessage.recipient_id == current_user.id))
    ).order_by(UserMessage.timestamp).all()
    return render_template('messages.html', messages=messages)


# User Pages

# Route: Logged In Page
@app.route('/user')
@user_required
def user_home():
    # Fetch only items that are NOT sold (expired items are still included)
    items = Item.query.filter(
        ~Item.item_id.in_(db.session.query(WaitingList.item_id)),
    ).all()

    # Get highest bid for each item
    item_bids = {item.item_id: item.highest_bid() for item in items}

    return render_template('user_home.html', pagetitle='User Home', items=items, item_bids=item_bids)

# Route: Search in navbar
@app.route('/user/search', methods = ['GET'])
@user_required
def search():
    search_query = request.args.get('query', '').strip()

    if not search_query:
        items = Item.query.all()
    else:
        items = Item.query.filter(Item.item_name.ilike(f"%{search_query}%")).all()

    item_bids = {}
    for item in items:
        highest_bid = db.session.query(db.func.max(Bid.bid_amount)).filter_by(item_id=item.item_id).scalar()
        item_bids[item.item_id] = highest_bid if highest_bid is not None else None 
    
    return render_template("user_home.html", items = items, item_bids = item_bids)

# Route: Watch
@app.route('/user/watch', methods=['POST'])
@user_required
def watch():
    """
    Handles AJAX request for watchlist
    """
    # Gets item id and if heart was clicked from json data
    data = request.get_json()
    watch = data.get('watch')
    item_id = data.get('item_id')

    item = Item.query.get(item_id)
    user = User.query.get(current_user.id)

    if watch == 1:
        # adds liked item to watchlist
        if item not in user.watchlist:
            user.watchlist.append(item)
        # allows for item to be unliked
        else:
            user.watchlist.remove(item)
    db.session.commit()
    
    return jsonify({'status':'OK','watch': watch}), 200

# Route: Sort items on main page
@app.route('/user/sort_items', methods=['GET'])
@user_required
def sort_items():
    """
    Handles json request to allow dynamic sort feature to sort items
    """
    # if user selects the sort function
    sort_by = request.args.get('sort', 'all')

    # query the items on the main page
    if sort_by == "min_price":
        sorted_items = Item.query.filter(
            ~Item.item_id.in_(db.session.query(WaitingList.item_id)),
        ).order_by(Item.minimum_price.asc()).all()
    elif sort_by == "name_asc":
        sorted_items = Item.query.filter(
            ~Item.item_id.in_(db.session.query(WaitingList.item_id)),
        ).order_by(Item.item_name.asc()).all()
    elif sort_by == "unexpired":
        items = Item.query.filter(
            ~Item.item_id.in_(db.session.query(WaitingList.item_id)), Item.sold == False).all()
        sorted_items = [item for item in items if item.time_left != 0]
    else:
        sorted_items = Item.query.filter(
            ~Item.item_id.in_(db.session.query(WaitingList.item_id)),
        ).all()

    item_bids = {item.item_id: item.highest_bid() for item in sorted_items}
    
    # Convert to JSON format
    # Convert to JSON format
    items = [{
        "item_id": item.item_id,
        "item_name": item.item_name,
        "minimum_price": str(item.minimum_price),
        "shipping_cost": str(item.shipping_cost),
        "item_image": item.item_image,
         "current_highest_bid": str(item_bids.get(item.item_id, "No bids yet")),
        "approved": item.approved,
        "expiration_time": str(item.expiration_time),
        "time_left" : item.time_left.total_seconds(),
        "seller_id" : item.seller_id,
        "is_watched": True
    } for item in sorted_items]

    return jsonify(items)

# Route: Account
@app.route('/user/account', methods=['GET', 'POST'])
@login_required
def account():
    """
    Redirects to account page, has buttons to other pages and user information.
    """
    sidebar_form = SideBarForm()

    if sidebar_form.validate_on_submit() :
        if sidebar_form.info.data:
            return redirect(url_for("account"))
        elif sidebar_form.my_bids.data:
            return redirect(url_for("my_bids"))
        elif sidebar_form.my_listings.data:
            return redirect(url_for("my_listings"))
        elif sidebar_form.watchlist.data:
            return redirect(url_for("watchlist"))
        elif sidebar_form.notifications.data:
            return redirect(url_for("notifications"))
        elif sidebar_form.logout.data:
            return redirect(url_for("logout")) 
    
    info_form = UserInfoForm()
    username_form = ChangeUsernameForm()
    email_form = ChangeEmailForm()
    password_form = ChangePasswordForm()
    card_form = CardInfoForm()
    edit_expertise_form = EditExpertiseForm()
    
    user = User.query.get(current_user.id)
    # find users payment and shipping info from PaymentInfo table 
    payment_info = PaymentInfo.query.filter(PaymentInfo.user_id == user.id).first()

    # Only access attributes if payment_info is not None
    if payment_info:  
        payment_type = payment_info.payment_type
        shipping_info = payment_info.shipping_address
    else:
        payment_type = None
        shipping_info = None
    
    # if user info is updated, update in db
    if info_form.update_info.data and info_form.validate_on_submit():
        user.first_name=info_form.first_name.data
        user.last_name=info_form.last_name.data
        db.session.commit()
        flash('Information updated successfully!', 'success')
    
    # if username is updated, validate then update in db
    if username_form.update_username.data and username_form.validate_on_submit():
        if User.query.filter_by(username=username_form.username.data).first():
            flash('Username already exists. Please choose a different one.', 'danger')
        else:
            user.username=username_form.username.data
            db.session.commit()
            flash('Username updated successfully!', 'success')

    # if email is updated, validate then update in db
    if email_form.update_email.data and email_form.validate_on_submit():
        if User.query.filter_by(email=email_form.email.data).first():
            flash('Email already exists. Please choose a different one.', 'danger')
        else:
            user.email=email_form.email.data
            db.session.commit()
            flash('Email updated successfully!', 'success')
    

    # if password is updated, update in db
    if password_form.update_privacy.data and password_form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(password_form.new_password.data)
        user.password = hashed_password
        db.session.commit()
        flash('Password updated successfully!', 'success')
    

    # validation error handeling
    if info_form.update_info.data and not info_form.validate_on_submit():
        flash('Invalid first or last name (only letters are allowed).', 'danger')

    if username_form.username.data and not username_form.validate_on_submit():
        flash('Invalid username.', 'danger')
    
    if email_form.email.data and not email_form.validate_on_submit():
        flash('Invalid email address.', 'danger')

    if password_form.update_privacy.data and not password_form.validate_on_submit():
        if password_form.new_password.data != password_form.confirm_password.data:
            flash('Passwords do not match.', 'danger')

    # if payment info is updated, update in db
    if card_form.update_card.data and card_form.validate_on_submit():
        # Update existing payment info for current user
        payment_info.payment_type = card_form.card_number.data
        payment_info.shipping_address = card_form.shipping_address.data
        db.session.commit()
        flash('Payment info updated successfully!', 'success')

    if edit_expertise_form.update_expertise.data and edit_expertise_form.validate_on_submit():
        current_user.expertise = edit_expertise_form.expertise.data
        print(edit_expertise_form.expertise.data)
        db.session.commit()
        flash('Expertise updated.', 'success')

    # populate forms with user information
    if request.method == 'GET' or not info_form.validate_on_submit() or not username_form.validate_on_submit() or not email_form.validate_on_submit() or not card_form.validate_on_submit() or not password_form.validate_on_submit():
        # user info
        info_form.first_name.data = user.first_name
        info_form.last_name.data = user.last_name

        username_form.username.data = user.username
        email_form.email.data = user.email

        # if info then print in form else dont print anything
        if payment_info:
            card_form.card_number.data = payment_info.payment_type
            card_form.shipping_address.data = payment_info.shipping_address
        else:
            card_form.card_number.data = None
            card_form.shipping_address.data = None

        edit_expertise_form.expertise.data = user.expertise


    return render_template('user_account.html', pagetitle='Account', sidebar_form=sidebar_form, info_form=info_form, 
        username_form=username_form, email_form=email_form, password_form=password_form, card_form=card_form, edit_expertise_form=edit_expertise_form)

# Route: My Bids
@app.route('/user/my_bids', methods=['GET', 'POST'])
@user_required
def my_bids():
    """
    Redirects to my listings page, has buttons to other pages.
    """
    form = SideBarForm()

    if form.validate_on_submit():
        if form.info.data:
            return redirect(url_for("account"))
        elif form.my_bids.data:
            return redirect(url_for("my_bids"))
        elif form.my_listings.data:
            return redirect(url_for("my_listings"))
        elif form.watchlist.data:
            return redirect(url_for("watchlist"))
        elif form.notifications.data:
            return redirect(url_for("notifications"))
        elif form.logout.data:
            return redirect(url_for("logout"))


    user = User.query.get(current_user.id)
    bidded_items = Item.query.join(Bid).filter(Bid.user_id == user.id).all()

    print(bidded_items)

    item_bids = {item.item_id: item.highest_bid() for item in bidded_items}

    return render_template('user_my_bids.html', pagetitle='Bidded Items', form=form, bidded_items=bidded_items, item_bids=item_bids)


# Route: My Listings
@app.route('/user/my_listings', methods=['GET', 'POST'])
@user_required
def my_listings():
    """
    Redirects to my listings page, has buttons to other pages.
    """
    form = SideBarForm()

    if form.validate_on_submit():
        if form.info.data:
            return redirect(url_for("account"))
        elif form.my_bids.data:
            return redirect(url_for("my_bids"))
        elif form.my_listings.data:
            return redirect(url_for("my_listings"))
        elif form.watchlist.data:
            return redirect(url_for("watchlist"))
        elif form.notifications.data:
            return redirect(url_for("notifications"))
        elif form.logout.data:
            return redirect(url_for("logout"))


    items = Item.query.filter_by(seller_id=current_user.id).all()

    item_bids = {item.item_id: item.highest_bid() for item in items}

    waiting_list = db.session.query(WaitingList.item_id).all()
    waiting_list = [item[0] for item in waiting_list]

    return render_template('user_my_listings.html', pagetitle='Listings', form=form, items=items, item_bids=item_bids, waiting_list = waiting_list)

# Route: Watchlist
@app.route('/user/watchlist', methods=['GET', 'POST'])
@user_required
def watchlist():
    """
    Redirects to watchlist page, has buttons to other pages.
    """
    form = SideBarForm()

    user = User.query.get(current_user.id)
    watched_items = user.watchlist

    if form.validate_on_submit():
        if form.info.data:
            return redirect(url_for("account"))
        elif form.my_bids.data:
            return redirect(url_for("my_bids"))
        elif form.my_listings.data:
            return redirect(url_for("my_listings"))
        elif form.watchlist.data:
            return redirect(url_for("watchlist"))
        elif form.notifications.data:
            return redirect(url_for("notifications"))
        elif form.logout.data:
            return redirect(url_for("logout"))

    item_bids = {item.item_id: item.highest_bid() for item in watched_items}

    return render_template('user_watchlist.html', pagetitle='Watchlist', form=form, watched_items=watched_items, item_bids=item_bids)

# Route: Sort watchlist items
@app.route('/user/sort_watchlist', methods=['GET'])
@user_required
def sort_watchlist():
    """
    Handles json request to allow dynamic sort feature to sort items
    """
    # if user selects the sort function
    sort_by = request.args.get('sort', 'all')

    # query the items in the user's watchlist
    items = db.session.query(Item).join(Watched_item).filter(Watched_item.c.user_id == current_user.id)

    item_bids = {item.item_id: item.highest_bid() for item in items}

    if sort_by == "min_price":
        sorted_items = items.order_by(Item.minimum_price.asc()).all()
    elif sort_by == "name_asc":
        sorted_items = items.order_by(Item.item_name.asc()).all()
    elif sort_by == "unexpired":
        items = db.session.query(Item).filter(Item.sold == False).all()
        sorted_items = [item for item in items if item.time_left != 0]
    else :
        sorted_items = items.all()

    # Convert to JSON format
    watched_items = [{
        "item_id": item.item_id,
        "item_name": item.item_name,
        "minimum_price": str(item.minimum_price),
        "shipping_cost": str(item.shipping_cost),
        "item_image": item.item_image,
        "current_highest_bid": str(item_bids.get(item.item_id, "No bids yet")),
        "approved": item.approved,
        "expiration_time": str(item.expiration_time) ,
        "time_left" : item.time_left.total_seconds(),
        "seller_id" : item.seller_id,
        "is_watched": True
    } for item in sorted_items]

    return jsonify(watched_items)

# Route: Notifications
@app.route('/user/notifications', methods=['GET', 'POST'])
@login_required
def notifications():
    """
    Redirects to my notifications page, has buttons to other pages.
    """
    form = SideBarForm()

    if form.validate_on_submit():
        if form.info.data:
            return redirect(url_for("account"))
        elif form.my_bids.data:
            return redirect(url_for("my_bids"))
        elif form.my_listings.data:
            return redirect(url_for("my_listings"))
        elif form.watchlist.data:
            return redirect(url_for("watchlist"))
        elif form.notifications.data:
            return redirect(url_for("notifications"))
        elif form.logout.data:
            return redirect(url_for("logout"))

    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.timestamp.desc()).all()
    db.session.commit()
 
    return render_template('user_notifications.html', pagetitle='Notifications', form=form, notifications=notifications)

# Route: Mark read notifications as read
@app.route('/mark_notifications_as_read')
@login_required
def mark_notifications_as_read():
    """
    Marks all unread notifications for the user as read.
    This is triggered AFTER the page has loaded.
    """
    unread_notifications = Notification.query.filter_by(user_id=current_user.id, read=False).all()

    for notification in unread_notifications:
        notification.read = True

    db.session.commit()

    # Return a blank response (so the browser doesn't show anything)
    return '', 204


# Route: Delete Notification
@app.route('/notification/delete/<int:notification_id>', methods=['GET', 'POST'])
@user_required
def delete_notification(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    
    # Ensure the current user owns this notification
    if notification.user_id != current_user.id:
        flash("You are not authorized to delete this notification.", "danger")
        return redirect(url_for('notifications'))
    
    db.session.delete(notification)
    db.session.commit()
    flash("Notification deleted.", "success")
    return redirect(url_for('notifications'))

# Route: List Item Page
@app.route('/user/list_item', methods=['GET', 'POST'])
@user_required
def user_list_item():
    form = ListItemForm()

    if form.validate_on_submit():
        # Ensure the upload folder exists
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

        # Process the uploaded image
        image_file = form.item_image.data
        if image_file and allowed_file(image_file.filename):
            filename = f"{uuid.uuid4().hex}_{secure_filename(image_file.filename)}"
            filepath = os.path.join(app.config['ITEM_IMAGE_FOLDER'], filename)
            image_file.save(filepath)
        elif image_file and not allowed_file(image_file.filename):
            flash('Invalid file type. Only images are allowed.', 'danger')
            return redirect(url_for('user_list_item', form=form))
        listing_time = datetime.utcnow()
        if 'authenticate' in request.form:
            date_time = None
            expiration_time = None
        else:
            date_time = datetime.utcnow()
            expiration_time = listing_time + timedelta(
                days=int(form.days.data),
                hours=int(form.hours.data),
                minutes=int(form.minutes.data)
            )

        # Store item in DB
        new_item = Item(
            seller_id=current_user.id,
            item_name=form.item_name.data,
            description=form.description.data,
            minimum_price=form.minimum_price.data,
            item_image=filename,
            date_time=date_time,
            expiration_time=expiration_time,
            days=int(form.days.data),
            hours=int(form.hours.data),
            minutes=int(form.minutes.data),
            shipping_cost=form.shipping_cost.data,
            approved=False,
            category=form.category.data
        )
        
        db.session.add(new_item)
        db.session.commit()
        
        if 'authenticate' in request.form:
            waiting_list_entry = WaitingList(item_id=new_item.item_id)
            db.session.add(waiting_list_entry)
            db.session.commit()
        else :
            flash('Item listed successfully!', 'success')
        return redirect(url_for('user_home'))
        
    return render_template('user_list_item.html', title='List Item', form=form)


# Route: For clicking on an item to see more detail
@app.route('/item/<int:item_id>')
def user_item_details(item_id):
    item = Item.query.get_or_404(item_id)
    form = BidForm()

    # Ensure expiration_time and date_time are not None
    if item.date_time is None:
        item.date_time = datetime.utcnow()  # Provide a default timestamp

    if item.expiration_time is None:
        item.expiration_time = datetime.utcnow() + timedelta(days=7)  # Example: 7 days from now

    # Get the current highest bid
    highest_bid = db.session.query(db.func.max(Bid.bid_amount)).filter_by(item_id=item_id).scalar() or "No bids yet"

    # Get highest bidder ID
    highest_bidder = Bid.query.filter_by(item_id=item_id, bid_amount=highest_bid).first()
    highest_bidder_id = highest_bidder.user_id if highest_bidder else None

    return render_template('user_item_details.html', form=form, item=item, highest_bid=highest_bid, highest_bidder_id=highest_bidder_id)

# Route: Placing a bid
@socketio.on('new_bid')
@user_required
def handle_new_bid(data):
    """Handle new bid via WebSocket."""
    item_id = data.get('item_id')
    bid_amount = float(data.get('bid_amount'))

    item = Item.query.get(item_id)
    if not item:
        emit('bid_error', {'message': 'Item not found!'}, room=request.sid)
        return

    # Check if the user is trying to bid on their own item
    if item.seller_id == current_user.id:
        emit('bid_error', {'message': 'You cannot bid on your own item!'}, room=request.sid)
        return
    
    # Check if the auction has expired
    if datetime.utcnow() > item.expiration_time:
        emit('bid_error', {'message': 'Bidding has ended for this item.'}, room=request.sid)
        return

    # Get the current highest bid
    highest_bid = item.highest_bid() or item.minimum_price
    previous_highest_bidder = item.highest_bidder()

    # Validate bid amount
    if bid_amount <= highest_bid:
        emit('bid_error', {'message': 'Your bid must be higher than the current highest bid!'}, room=request.sid)
        return

    # Save new bid
    new_bid = Bid(
        item_id=item_id,
        user_id=current_user.id,
        bid_amount=bid_amount,
        bid_date_time=datetime.utcnow()
    )
    db.session.add(new_bid)

    # Notify the previous highest bidder if they were outbid
    if previous_highest_bidder and previous_highest_bidder.id != current_user.id:
        notification = Notification(
            user_id=previous_highest_bidder.id,
            message=f"You have been outbid on '{item.item_name}'. The new highest bid is £{bid_amount:.2f}."
        )
        db.session.add(notification)

    db.session.commit()

    # Notify all users of the new highest bid
    emit('update_bid', {'item_id': item_id, 'new_bid': bid_amount})

    # Notify the bidder that the bid was successful
    emit('bid_success', {'message': 'Bid placed successfully!'}, room=request.sid)



# Expert Pages

#Route: Expert Assignments Page
@app.route('/expert/assignments')
@expert_required
def expert_assignments():
    # Fetch items assigned to the current expert AND in the waiting list
    assigned_items = Item.query.filter(
        Item.expert_id == current_user.id,
        Item.item_id.in_(db.session.query(WaitingList.item_id))
    ).all()

    return render_template('expert_assignments.html', items=assigned_items)


#Route: Expert Authentication Page
@app.route('/expert/item_authentication/<int:item_id>')
@expert_required
def expert_item_authentication(item_id):

    item_to_authenticate = Item.query.get(item_id)
    experts = User.query.filter(User.priority == 2)
    return render_template('expert_item_authentication.html', item_to_authenticate=item_to_authenticate, experts=experts)

@app.route('/expert/approve_item/<int:item_id>', methods=['POST'])
@expert_required
def approve_item(item_id):

    item_to_approve = Item.query.get(item_id)
    # Approve item
    item_to_approve.approved = True
    # Set start and expiration time
    date_time = datetime.utcnow()
    item_to_approve.expiration_time = datetime.utcnow() + timedelta(
        days=item_to_approve.days,
        hours=item_to_approve.hours,
        minutes=item_to_approve.minutes
    )
    
    
    # Remove from waiting list
    WaitingList.query.filter_by(item_id=item_id).delete()

    db.session.commit()

    flash("Item approved successfully.", "success")
    return redirect(url_for('expert_assignments'))

@app.route('/expert/decline_item/<int:item_id>', methods=['POST'])
@expert_required
def decline_item(item_id):

    item_to_approve = Item.query.get(item_id)
    # Reject item
    item_to_approve.approved = False
    # Set expiration time
    item_to_approve.expiration_time = datetime.utcnow() + timedelta(
        days=item_to_approve.days,
        hours=item_to_approve.hours,
        minutes=item_to_approve.minutes
    )
    # Remove from waiting list
    WaitingList.query.filter_by(item_id=item_id).delete()

    db.session.commit()
    flash("Item rejected successfully.", "success")
    return redirect(url_for('expert_assignments'))

# Route: Reassign item button
@app.route('/expert/reassign_item/<int:item_id>', methods=['POST'])
@expert_required
def reassign_item(item_id):
    """
    Removes the assigned expert from an item, making it available for reassignment.
    """
    item_to_be_reassigned = Item.query.get(item_id)

    # Remove the expert assignment
    item_to_be_reassigned.expert_id = None

    db.session.commit()
    flash("Expert unassigned successfully.", "warning")

    return redirect(url_for('expert_assignments'))

# i dont think this is needed
@app.route('/expert/message_seller/<int:item_id>', methods=['GET', 'POST'])
@expert_required
def expert_message_seller(item_id):
    """
    Allows an expert to send a private message to the seller of an item.
    """
    item = Item.query.get_or_404(item_id)
    seller = item.seller  # Retrieve the seller's user object

    if request.method == 'POST':
        message_content = request.form.get('message')

        if message_content:
            new_message = UserMessage(
                sender_id=current_user.id,
                recipient_id=seller.id,
                content=message_content
            )
            db.session.add(new_message)
            db.session.commit()
            flash("Message sent successfully!", "success")
            return redirect(url_for('expert_assignments'))

    return render_template('expert_messaging.html', item=item, seller=seller)

# Route: Inbox for all users
@app.route('/inbox')
@login_required
def inbox():
    """
    Display unique conversations where the logged-in user is involved.
    Show the most recent message for each sender-item combination,
    even if the user was the sender and has not received a reply yet.
    """
    # Get the latest message from each user-item combination
    latest_messages = db.session.query(
        UserMessage.sender_id,
        UserMessage.recipient_id,
        UserMessage.item_id,
        db.func.max(UserMessage.timestamp).label('latest_time')
    ).filter(
        (UserMessage.recipient_id == current_user.id) | (UserMessage.sender_id == current_user.id)  # Include both sent and received messages
    ).group_by(UserMessage.sender_id, UserMessage.recipient_id, UserMessage.item_id) \
     .subquery()

    # Fetch actual messages using the latest timestamp
    messages = db.session.query(UserMessage).join(
        latest_messages,
        (UserMessage.sender_id == latest_messages.c.sender_id) &
        (UserMessage.recipient_id == latest_messages.c.recipient_id) &
        (UserMessage.item_id == latest_messages.c.item_id) &
        (UserMessage.timestamp == latest_messages.c.latest_time)
    ).order_by(UserMessage.timestamp.desc()).all()

    return render_template('inbox.html', messages=messages)

# Route: Chat
@app.route('/chat/<int:user_id>/', defaults={'item_id': None}, methods=['GET', 'POST'])
@app.route('/chat/<int:user_id>/<int:item_id>', methods=['GET', 'POST'])
@login_required
def chat(user_id, item_id):
    """
    Show conversation history with a specific user.
    Optional: filter by item.
    """
    recipient = User.query.get_or_404(user_id)

    # Only fetch item if item_id is provided (avoid .get(None) warning)
    item = None
    if item_id is not None:
        item = Item.query.get_or_404(item_id)

    # Build query for messages between the two users
    message_query = UserMessage.query.filter(
        ((UserMessage.sender_id == current_user.id) & (UserMessage.recipient_id == user_id)) |
        ((UserMessage.sender_id == user_id) & (UserMessage.recipient_id == current_user.id))
    )

    # Filter by item_id or lack thereof
    if item_id is not None:
        message_query = message_query.filter(UserMessage.item_id == item_id)
    else:
        message_query = message_query.filter(UserMessage.item_id == None)

    messages = message_query.order_by(UserMessage.timestamp).all()

    # Mark unread messages as read
    unread_query = UserMessage.query.filter(
        UserMessage.sender_id == user_id,
        UserMessage.recipient_id == current_user.id,
        UserMessage.read == False
    )

    if item_id is not None:
        unread_query = unread_query.filter(UserMessage.item_id == item_id)
    else:
        unread_query = unread_query.filter(UserMessage.item_id == None)

    unread_messages = unread_query.all()
    for msg in unread_messages:
        msg.read = True

    db.session.commit()

    # Handle reply submission
    if request.method == "POST":
        message_content = request.form.get("message")
        if message_content:
            new_message = UserMessage(
                sender_id=current_user.id,
                recipient_id=user_id,
                item_id=item_id,
                subject=item.item_name if item else None,
                content=message_content,
                read=False
            )
            db.session.add(new_message)

            # Create notification
            notification = Notification(
                user_id=user_id,
                message=f"You have a new message from {current_user.username}."
            )
            db.session.add(notification)

            db.session.commit()
            return redirect(url_for('chat', user_id=user_id, item_id=item_id) if item_id else url_for('chat', user_id=user_id))

    return render_template('chat.html', messages=messages, recipient=recipient, item=item)

#Route: Expert Messaging Page
@app.route('/expert/messaging')
@expert_required
def expert_messaging():
    return render_template('expert_messaging.html')

#Route: Expert Avaliablity Page
@app.route('/expert/availability',methods=['POST','GET'])
@expert_required
def expert_availability():

    user_id = current_user.id
    if request.method == "POST":

        dates = request.form.get('date')
        start_times = request.form.get('start_time')

        ExpertAvailabilities.query.filter_by(user_id=user_id).delete()
        
        if not dates and not start_times:
            db.session.commit()
            return redirect(url_for('expert_availability'))

        splitDates = dates.split(",")
        splitStartTimes =start_times.split(",")

        for date, start_time, in zip(splitDates, splitStartTimes, ):
            date_obj = datetime.strptime(date, '%Y-%m-%d').date()

            start_time_obj = datetime.strptime(start_time, '%H:%M').time()

            availability = ExpertAvailabilities(
                user_id=user_id,
                date=date_obj,
                start_time=start_time_obj,
                duration=1
            )

            db.session.add(availability)

        db.session.commit()
        return redirect(url_for('expert_availability'))

    else:

        availabilites = ExpertAvailabilities.query.filter_by(user_id=user_id).all()

        filled_timeslots = []

        for timeslot in availabilites:
            filled_timeslots.append({"date": str(timeslot.date), "start_time":str(timeslot.start_time)[:5]})


        return render_template('expert_availability.html',filled_timeslots=filled_timeslots)

@app.route('/expert/account')
@expert_required
def expert_account():
    # Fetch items assigned to the current expert that are NOT in the waiting list
    assigned_items = Item.query.filter(
        Item.expert_id == current_user.id,
        ~Item.item_id.in_(db.session.query(WaitingList.item_id))
    ).all()

    # Categorise items into approved and rejected
    approved_items = [item for item in assigned_items if item.approved is True]
    rejected_items = [item for item in assigned_items if item.approved is False]

    return render_template(
        'expert_account.html',
        approved_items=approved_items,
        rejected_items=rejected_items
    )


# Manager Pages

# Route: Managers Home
# Remove
@app.route('/manager')
@manager_required
def manager_home():
    """
    Redirects to managers home page when website first opened.
    """
    return render_template('manager_home.html')


#Route: Manager Stats Page
@app.route('/manager/statistics', methods=['GET','POST'])
@manager_required
def manager_statistics():

    bids = Bid.query.all()

    total_revenue = 0
    total_profit = 0

    sold_items = SoldItem.query.all()

    for sold_item in sold_items:
        total_revenue += sold_item.price 

    items = Item.query.all()
    
    if items:
        generated_percentage = items[0].site_fee_percentage
    else:
        generated_percentage = 1

    for item in items:
        if item.sold_item:
            final_price = item.sold_item[0].price
            site_fee = item.calculate_fee(final_price, expert_approved=False)
            total_profit += site_fee


    current_date = datetime.now()
    three_weeks_ago = current_date - timedelta(weeks=3)

    weeks = []
    values = []

    for i in range(4):
        week_start = three_weeks_ago + timedelta(weeks=i)
        week_end = week_start + timedelta(days = 6,hours=23,minutes=59,seconds=59)

        expired_items = Item.query.filter(
            Item.expiration_time >= week_start,
            Item.expiration_time <= week_end            
        ).all()

        weekly_revenue = 0

        for item in expired_items:
            if item.sold_item:
                for sold_item in item.sold_item:
                    final_price = sold_item.price
                    site_fee = item.calculate_fee(final_price, expert_approved=False)
                    weekly_revenue += site_fee

        values.append(weekly_revenue)

        weeks.append({
            'week_start': week_start.strftime('%m-%d'),
            'week_end': week_end.strftime('%m-%d')
        })


    week_labels = []

    for week in weeks:
        week_labels.append(f"{week['week_start']} - {week['week_end']}")    


    plt.figure(figsize=(10,6))

    plt.bar(week_labels, values,label='Weekly Revenue')
    plt.autoscale(axis='y')

    plt.legend()

    plt.xlabel('Week')
    plt.ylabel('GBP')


    img = io.BytesIO()
    plt.savefig(img,format='png')
    img.seek(0)

    ratio = [0.75]

    img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')

    return render_template('manager_statistics.html', img_data=img_base64, ratio=ratio, week_labels=week_labels,values=values,total_revenue=total_revenue,total_profit=total_profit,generated_percentage=generated_percentage)


# FIXME - choose a maethod of selecting expert fee
@app.route('/manager/statistics/edit',methods=['GET','POST'])
@manager_required
def manager_statistics_edit():

    if request.method == 'POST':
        cost_site = request.form.get('site')
        cost_expert = request.form.get('expert')

        items = Item.query.all()

        if items:
            for item in items:
                if cost_site:
                    item.site_fee_percentage = float(cost_site)
                if cost_expert:
                    item.expert_fee_percentage = float(cost_expert)

            db.session.commit()
        return redirect(url_for('manager_statistics'))

    return render_template('manager_statistics.html')

# FIXME - choose a maethod of selecting expert fee

@app.route('/manager/statistics/cost',methods=['GET','POST'])
@manager_required
def manager_statistics_cost():

    total_revenue = 0
    total_profit = 0

    sold_items = SoldItem.query.all()

    for sold_item in sold_items:
        total_revenue += sold_item.price 

    items = Item.query.all()

    for item in items:
        if item.sold_item:
            final_price = item.sold_item[0].price
            site_fee = item.calculate_fee(final_price, expert_approved=False)
            total_profit += site_fee
    
    if items:
        generated_percentage = items[0].site_fee_percentage
    else:
        generated_percentage = 1


    sold_items = SoldItem.query.all()

    current_date = datetime.now()
    three_weeks_ago = current_date - timedelta(weeks=3)

    weeks = []
    expert_fee_value = []
    cost_value = []

    for i in range(4):
        week_start = three_weeks_ago + timedelta(weeks=i)
        week_end = week_start + timedelta(days = 6,hours=23,minutes=59,seconds=59)


        expired_items = Item.query.filter(
            Item.expiration_time >= week_start,
            Item.expiration_time <= week_end            
        ).all()


        weekly_expert_fee = 0
        item_cost = 0

        for item in expired_items:
            if item.sold_item:
                for sold_item in item.sold_item:
                        final_price = sold_item.price
                        site_fee = item.calculate_fee(final_price,expert_approved=False)

                        if item.approved:                        
                    
                            expert_fee = item.calculate_fee(final_price,expert_approved=True) - site_fee
                            weekly_expert_fee += expert_fee

                            item_cost = final_price - (expert_fee + site_fee)
                        else:
                            item_cost += final_price - site_fee
                            weekly_expert_fee = 0

        expert_fee_value.append(weekly_expert_fee)
        cost_value.append(item_cost)
                        
        weeks.append({
            'week_start': week_start.strftime('%m-%d'),
            'week_end': week_end.strftime('%m-%d')
        })

    week_labels = []

    for week in weeks:
        week_labels.append(f"{week['week_start']} - {week['week_end']}")    

    plt.figure(figsize=(10,6))

    x=np.arange(len(expert_fee_value))

    plt.bar(week_labels, expert_fee_value, label='Expert Fee')
    plt.bar(week_labels, cost_value, bottom = expert_fee_value, label='Item Cost')
    plt.autoscale(axis='y')
    plt.legend()

    plt.xlabel('Week')
    plt.ylabel('GBP')

    img = io.BytesIO()
    plt.savefig(img,format='png')
    img.seek(0)

    ratio = [0.75]

    img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')


    return render_template('manager_statistics_cost.html',img_data = img_base64, total_profit = total_profit, total_revenue = total_revenue, generated_percentage=generated_percentage)

#Route: Manager Account Page
@app.route('/manager/accounts',methods=['GET','POST'])
@manager_required
def manager_accounts():
    page = request.args.get('page',1,type=int)
    
    accounts = User.query.paginate(page=page,per_page=5,error_out=False)

    return render_template("manager_accounts.html",accounts=accounts)

#Route: Updates priority
@app.route('/manager/accounts/<username>/<int:update_number>',methods=['GET','POST'])
@manager_required
def manager_accounts_update_number(username,update_number):

    account = User.query.filter_by(username=username).first()
    
    if account and (1<= update_number <=3) :
        account.priority = update_number
        if update_number == 2:
            account.expertise = "other"
        else:
            account.expertise = None
        db.session.commit()

        return redirect(url_for('manager_accounts'))
    else:
        return "Error", 404

#Route: Sorts Accounts
@app.route('/manager/accounts/sort/low_high',methods=['GET','POST'])
@manager_required
def manager_accounts_sort_low_high():
    accounts = User.query.order_by(User.username).all()
    return render_template('manager_accounts.html',accounts = accounts)

#Route: Sorts Accounts
@app.route('/manager/accounts/sort/high_low',methods=['GET','POST'])
@manager_required
def manager_accounts_sort_high_low():
    accounts = User.query.order_by(desc(User.username)).all()
    return render_template('manager_accounts.html',accounts = accounts)

#Route: Filters Accounts by Priority
@app.route('/manager/accounts/filter/<int:filter_number>',methods=['GET','POST'])
@manager_required
def manager_accounts_filter(filter_number):
    filtered_accounts = User.query.filter(User.priority == filter_number).all()

    if not filtered_accounts:
        filtered_accounts = []

    return render_template("manager_accounts.html",accounts = filtered_accounts) 
   
#Route: Sorts Accounts
@app.route('/manager/accounts/search',methods = ['GET'])
@manager_required
def manager_accounts_search():
    search_query = request.args.get('query', '')
    filtered_accounts = []
    empty_accounts = []

    accounts = User.query.all()

    if not search_query:
        return render_template("manager_accounts.html",accounts = empty_accounts)

    for account in accounts:
        if search_query.lower() == account.username.lower():
            filtered_accounts.append(account)
    
    return render_template("manager_accounts.html",accounts=filtered_accounts)

#Route: Manager Listing Page
@app.route('/manager/listings',methods=['GET','POST'])
@manager_required
def manager_listings():
    items = Item.query.all()
    return render_template("manager_listings.html",items = items)

#Route: Manager User Details Page
@app.route('/manager/listings/<int:id>',methods=['GET'])
@manager_required
def manager_lisgings_user(id):
    user = User.query.get(id)
    user_listings = user.items
    return render_template("manager_listings_user.html", account = user, items=user_listings)   

#Route: Update priority through user details page
@app.route('/manager/listings/<int:id>/<int:update_number>',methods=['GET','POST'])
@manager_required
def manager_listings_update_number(username,update_number):
    user_account = User.query.filter_by(id=id).first()

    if user_account:
        user_account.priority = update_number
        db.session.commit()

        return render_template("manager_listings.html",account = user_account)
    else:
        return "User not found", 404

#Route: Manager look for avalibale experts Page
@app.route('/manager/expert_availability')
@manager_required
def manager_expert_availability():

    experts = User.query.filter_by(priority=2).all()

    current_time = datetime.utcnow()
    time_threshold = current_time + timedelta(hours=48)

    # Store experts available in the next 48 hours
    available_experts_48h = set(
        slot.user_id
        for slot in ExpertAvailabilities.query.filter(
            ExpertAvailabilities.date >= current_time.date(),
            ExpertAvailabilities.date <= time_threshold.date()
        ).all()
    )

    expert_availability = {
        expert.id: [
            {
                "id": slot.availability_id,
                "date": slot.date.strftime("%Y-%m-%d"),
                "start_time": slot.start_time.strftime("%I:%M %p"),
                "duration": slot.duration
            } for slot in ExpertAvailabilities.query.filter_by(user_id=expert.id).all()
        ] for expert in experts
    }

    assigned_items = (
        db.session.query(Item)
        .join(WaitingList, Item.item_id == WaitingList.item_id)
        .filter(Item.expert_id.isnot(None))
        .all()
    )


    # Fetch only items that are in the WaitingList
    unassigned_items = (
        db.session.query(Item)
        .join(WaitingList, Item.item_id == WaitingList.item_id)
        .filter(Item.expert_id.is_(None))
        .all()
    )

    # Fetch approved and rejected items that are assigned to an expert AND NOT in the Waiting List
    approved_items = (
        db.session.query(Item)
        .filter(
            Item.expert_id.isnot(None),
            Item.approved.is_(True),
            ~Item.item_id.in_(db.session.query(WaitingList.item_id))  # Exclude items in WaitingList
        )
        .all()
    )

    rejected_items = (
        db.session.query(Item)
        .filter(
            Item.expert_id.isnot(None),
            Item.approved.is_(False),
            ~Item.item_id.in_(db.session.query(WaitingList.item_id))  # Exclude items in WaitingList
        )
        .all()
    )

    return render_template(
        'manager_expert_availability.html',
        experts=experts,
        available_experts_48h=available_experts_48h,
        expert_availability=expert_availability,
        assigned_items=assigned_items,
        unassigned_items=unassigned_items,
        approved_items=approved_items,
        rejected_items=rejected_items,
        category_choices=CATEGORY_CHOICES
)

#Route: Assign an expert
@app.route('/assign_expert', methods=['POST'])
@manager_required
def assign_expert():
    expert_id = request.form.get('selected_expert')
    item_id = request.form.get('item_id')
    selected_time_id = request.form.get('selected_time')
    expert_fee_percentage = request.form.get('expert_fee_percentage', type=float)

    item = Item.query.get(item_id)
    selected_time = ExpertAvailabilities.query.filter_by(availability_id=selected_time_id, user_id=expert_id).first()

    if item and selected_time:
        item.expert_id = expert_id
        item.date_time = datetime.combine(selected_time.date, selected_time.start_time)  # FIXED: Set date_time
        item.expert_fee_percentage = expert_fee_percentage  # Save the percentage
        
        db.session.delete(selected_time)  # Remove from availability

        notification = Notification(
            user_id=expert_id,
            message=f"You have been assigned to authenticate the item '{item.item_name}'."
        )
        db.session.add(notification)
        db.session.commit()

        flash(f'Expert assigned successfully for {item.date_time.strftime("%Y-%m-%d %I:%M %p")}', 'success')

    else:
        flash("Failed to assign expert. Please select an available time slot.", "danger")

    return redirect(url_for('manager_expert_availability'))

#Route: Unassign an expert
@app.route('/unassign_expert', methods=['POST'])
@manager_required
def unassign_expert():
    item_id = request.form.get('item_id')
    item = Item.query.get(item_id)

    if item and item.expert_id:
        # Restore the expert's availability
        restored_availability = ExpertAvailabilities(
            user_id=item.expert_id,
            date=item.date_time.date(),
            start_time=item.date_time.time(),
            duration=1
        )
        db.session.add(restored_availability)

        # Remove expert assignment
        item.expert_id = None
        item.date_time = None

        notification = Notification(
            user_id=expert_id,  
            message=f"You have been assigned to authenticate the item '{item.item_name}'."
        )

        db.session.add(notification)

        db.session.commit()
        
        flash('Expert unassigned successfully! Item has been added back to the waiting list.', 'warning')

    return redirect(url_for('manager_expert_availability'))


#Route: Manager view of Items that are approved, recycled, and pending items
@app.route('/manager/overview')
@manager_required
def manager_overview():
    return render_template('manager_overview.html',
                           userName="",
                           userPriority="",
                           userEmail="",
                           userCategory="",
                           approved_items=[],
                           rejected_items=[],
                           pending_items=[])

#Route: Update expert payment
@app.route('/update_expert_payment', methods=['POST'])
@manager_required
def update_expert_payment():
    if current_user.priority < 2:
        flash("Unauthorized Action", "danger")
        return redirect(url_for('index'))

    item_id = request.form.get('item_id')
    expert_fee_percentage = request.form.get('expert_fee_percentage', type=float)

    item = Item.query.get(item_id)

    if item and item.expert_id:  # Ensure the item is assigned to an expert
        item.expert_fee_percentage = expert_fee_percentage
        db.session.commit()
        flash(f'Expert payment percentage updated to {expert_fee_percentage}%', 'success')

    return redirect(url_for('manager_expert_availability'))

#FIXME what is this for
@app.route('/manager/fees', methods=['GET', 'POST'])
@manager_required
def manager_fees():
    fee_config = FeeConfig.get_current_fees()
    
    if request.method == 'POST':
        site_fee = request.form.get('site_fee', type=float)
        expert_fee = request.form.get('expert_fee', type=float)

        if site_fee is not None and expert_fee is not None:
            fee_config.site_fee_percentage = site_fee
            fee_config.expert_fee_percentage = expert_fee
            db.session.commit()
            print(f"Updated Fees: Site - {fee_config.site_fee_percentage}%, Expert - {fee_config.expert_fee_percentage}%")  # Debugging
            flash("Fees updated successfully!", "success")
            
    return render_template("manager_fees.html", fee_config=fee_config)

# STRIPE
# Route: Payment for item using stripe route
@app.route('/pay/<int:item_id>', methods=['POST'])
@user_required
def pay_for_item(item_id):
    """
    Creates a Stripe Checkout Session for the highest bidder,
    including shipping cost and expert fee (if applicable) in the total payment amount.
    """
    item = Item.query.get_or_404(item_id)

    # Get highest bid
    highest_bid = db.session.query(db.func.max(Bid.bid_amount)).filter_by(item_id=item_id).scalar()
    winning_bid = Bid.query.filter_by(item_id=item_id, bid_amount=highest_bid).first()

    # Ensure the current user is the highest bidder
    if not winning_bid or winning_bid.user_id != current_user.id:
        flash("You are not the winning bidder!", "danger")
        return redirect(url_for('user_item_details', item_id=item_id))

    # Convert values to float for proper calculations
    bid_price = float(highest_bid)
    shipping_price = float(item.shipping_cost)

    # Check if expert authentication is required
    if item.expert_id:
        expert_fee = bid_price * (item.expert_fee_percentage / 100)
    else:
        expert_fee = 0.0  # No expert fee if authentication isn't required

    # Calculate total checkout cost (Winning Bid + Shipping Cost + Expert Fee)
    total_price = bid_price + shipping_price + expert_fee

    # Create Stripe Checkout Session
    try:
        line_items = [
            {
                'price_data': {
                    'currency': 'gbp',
                    'product_data': {'name': item.item_name},
                    'unit_amount': int(bid_price * 100),  # Convert bid price to pence
                },
                'quantity': 1,
            },
            {
                'price_data': {
                    'currency': 'gbp',
                    'product_data': {'name': 'Shipping Cost'},
                    'unit_amount': int(shipping_price * 100),  # Convert shipping price to pence
                },
                'quantity': 1,
            }
        ]

        # Add expert fee only if applicable
        if expert_fee > 0:
            line_items.append({
                'price_data': {
                    'currency': 'gbp',
                    'product_data': {'name': 'Expert Fee'},
                    'unit_amount': int(expert_fee * 100),  # Convert expert fee to pence
                },
                'quantity': 1,
            })

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=url_for('payment_success', item_id=item_id, _external=True),
            cancel_url=url_for('user_item_details', item_id=item_id, _external=True),
        )
        return jsonify({'checkout_url': session.url})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Success route
@app.route('/payment_success/<int:item_id>')
@user_required
def payment_success(item_id):
    item = Item.query.get_or_404(item_id)

    # Find the highest bid for the item
    highest_bid = db.session.query(db.func.max(Bid.bid_amount)).filter_by(item_id=item_id).scalar()
    winning_bid = Bid.query.filter_by(item_id=item_id, bid_amount=highest_bid).first()

    # Ensure only the winning bidder can mark the item as sold
    if winning_bid and winning_bid.user_id == current_user.id:
        # Mark item as sold
        item.sold = True
        db.session.commit()

        # Add the item to SoldItem table
        sold_item = SoldItem(
            item_id=item_id,
            seller_id=item.seller_id,
            buyer_id=current_user.id,
            price=highest_bid
        )
        db.session.add(sold_item)
        db.session.commit()

        return render_template("payment_success.html", item=item, price=highest_bid)
    
    else:
        flash("Payment failed or unauthorized access.", "danger")
        return redirect(url_for('user_home'))


# API to fetch get remaining time on auction for an item in real time
@app.route('/get_time_left/<int:item_id>')
def get_time_left(item_id):
    """
    API to fetch remaining time for an item.
    """
    item = Item.query.get_or_404(item_id)
    
    # Calculate remaining time
    if item.time_left.total_seconds() > 0:
        time_left = f"{item.time_left.days} days, {item.time_left.seconds // 3600} hours, {(item.time_left.seconds // 60) % 60} minutes, {item.time_left.seconds % 60} seconds"
    else:
        time_left = "Expired"

    return jsonify({"time_left": time_left})






