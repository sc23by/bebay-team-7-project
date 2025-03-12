from app import app, db, bcrypt
from flask import render_template, redirect, url_for, request, flash, current_app, jsonify
from flask_login import login_user, current_user, login_required,logout_user
from app.forms import RegistrationForm, LoginForm, SideBarForm, UserInfoForm, ChangeUsernameForm, ChangeEmailForm, ChangePasswordForm, CardInfoForm, ListItemForm, BidForm
from app.models import FeeConfig, User, Item, Bid, WaitingList, ExpertAvailabilities, Watched_item, PaymentInfo,SoldItem
from functools import wraps
import matplotlib.pyplot as plt
import io
import base64
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime, timedelta
from sqlalchemy import desc
# Parses data sent by JS
import json

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


# User Pages

# Route: Logged In Page
@app.route('/user')
@user_required
def user_home():
    """
    Redirects to main page when website first opened. Displays only items not in waiting list.
    """
    items = Item.query.filter(
        ~Item.item_id.in_(db.session.query(WaitingList.item_id)),
    ).all()
        
    return render_template('user_home.html', pagetitle='User Home', items = items)

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
        sorted_items = Item.query.order_by(Item.minimum_price.asc()).all()
    elif sort_by == "name_asc":
        sorted_items = Item.query.order_by(Item.item_name.asc()).all()
    else:
        sorted_items = Item.query.all()

    # Convert to JSON format
    items = [{
        "item_id": item.item_id,
        "item_name": item.item_name,
        "description": item.description,
        "minimum_price": str(item.minimum_price),  # Convert Decimal to string
        "shipping_cost": str(item.shipping_cost), 
        "item_image": item.item_image,
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
        if password_form.new_password.data != password_form.confirm_password.data:
            flash('Passwords do not match.', 'danger')
        else:
            hashed_password = bcrypt.generate_password_hash(password_form.new_password.data)
            user.password = hashed_password
            db.session.commit()
            flash('Password updated successfully!', 'success')

    # if payment info is updated, update in db
    if card_form.update_card.data and card_form.validate_on_submit():
        # Update existing payment info for current user
        payment_info.payment_type = card_form.card_number.data
        payment_info.shipping_address = card_form.shipping_address.data

        db.session.commit()
        flash('Payment info updated successfully!', 'success')

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

    return render_template('user_account.html', pagetitle='Account', sidebar_form=sidebar_form, info_form=info_form, 
        username_form=username_form, email_form=email_form, password_form=password_form, card_form=card_form)

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
        elif form.my_listings.data:
            return redirect(url_for("my_listings"))
        elif form.watchlist.data:
            return redirect(url_for("watchlist"))
        elif form.notifications.data:
            return redirect(url_for("notifications"))
        elif form.logout.data:
            return redirect(url_for("logout"))

    return render_template('user_my_listings.html', pagetitle='Listings', form=form)

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
        elif form.my_listings.data:
            return redirect(url_for("my_listings"))
        elif form.watchlist.data:
            return redirect(url_for("watchlist"))
        elif form.notifications.data:
            return redirect(url_for("notifications"))
        elif form.logout.data:
            return redirect(url_for("logout"))

    return render_template('user_watchlist.html', pagetitle='Watchlist', form=form, watched_items = watched_items)

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

    if sort_by == "min_price":
        sorted_items = items.order_by(Item.minimum_price.asc()).all()
    elif sort_by == "name_asc":
        sorted_items = items.order_by(Item.item_name.asc()).all()
    else:
        sorted_items = items.all()

    # Convert to JSON format
    Watched_items = [{
        "item_id": item.item_id,
        "item_name": item.item_name,
        "minimum_price": str(item.minimum_price),  # Convert Decimal to string
        "date_time": item.date_time.strftime('%H:%M'),
        "item_image": item.item_image,
        "is_watched": True
    } for item in sorted_items]

    return jsonify(Watched_items)

# Route: Notifications
@app.route('/user/notifications', methods=['GET', 'POST'])
@user_required
def notifications():
    """
    Redirects to my notifications page, has buttons to other pages.
    """
    form = SideBarForm()

    if form.validate_on_submit():
        if form.info.data:
            return redirect(url_for("account"))
        elif form.my_listings.data:
            return redirect(url_for("my_listings"))
        elif form.watchlist.data:
            return redirect(url_for("watchlist"))
        elif form.notifications.data:
            return redirect(url_for("notifications"))
        elif form.logout.data:
            return redirect(url_for("logout"))

    return render_template('user_notifications.html', pagetitle='Notifications', form=form)

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
            approved=False
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
    item = Item.query.get_or_404(item_id)  # Fetch the item or return 404
    form=BidForm()

    highest_bid = db.session.query(db.func.max(Bid.bid_amount)).filter_by(item_id=item_id).scalar()
    
    return render_template('user_item_details.html', form=form, item=item, highest_bid=highest_bid)

# Route: Placing a bid
@app.route('/item/<int:item_id>/bid', methods=['GET', 'POST'])
@user_required
def place_bid(item_id):
    item = Item.query.get_or_404(item_id)
    form = BidForm()

    # Check if the auction has expired
    if datetime.utcnow() > item.expiration_time:
        flash("Bidding has ended for this item.", "danger")
        return redirect(url_for('user_item_details', item_id=item_id))

    # Get the current highest bid
    highest_bid = db.session.query(db.func.max(Bid.bid_amount)).filter_by(item_id=item_id).scalar() or item.minimum_price

    if form.validate_on_submit():
        bid_amount = form.bid_amount.data

        # Check if bid is valid
        if bid_amount <= highest_bid:
            flash("Your bid must be higher than the current highest bid!", "danger")
        else:
            new_bid = Bid(
                item_id=item_id,
                user_id=current_user.id,
                bid_amount=bid_amount,
                bid_date_time=datetime.utcnow()
            )
            db.session.add(new_bid)
            db.session.commit()
            flash("Bid placed successfully!", "success")
            return render_template('user_item_details.html', form=form, item=item, highest_bid=highest_bid)


    highest_bid = db.session.query(db.func.max(Bid.bid_amount)).filter_by(item_id=item_id).scalar() or item.minimum_price
    
    return render_template('user_item_details.html', form=form, item=item, highest_bid=highest_bid)




# Expert Pages

#Route: Expert Assignments Page
@app.route('/expert/assignments')
@expert_required
def expert_assignments():
    return render_template('expert_assignments.html')

#Route: Expert Authentication Page
@app.route('/expert/item_authentication')
@expert_required
def expert_item_authentication():
    return render_template('expert_item_authentication.html')

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
        return render_template('expert_availability.html')

#Route: Expert Account Page
@app.route('/expert/account')
@expert_required
def expert_account():
    return render_template('expert_account.html')

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
    date_str = request.args.get('date',default = '2025-03-01', type = str)
    start_date = datetime.strptime(date_str, '%Y-%m-%d')

    weeks = []

    current_date = start_date
    while current_date.weekday() != 6:
        current_date -= timedelta(days = 1)

    for i in range(4):
        week_start = current_date
        week_end = current_date + timedelta(days = 6)
        weeks.append({
            'week_start': week_start.strftime('%Y-%m-%d'),
            'week_end' : week_end.strftime('%Y-%m-%d') 
        })

        current_date = week_end + timedelta(days=1)

    week_labels = []

    for week in weeks:
        week_labels.append(f"{week['week_start']} - {week['week_end']}")
    print(week_labels)
    values = [100,150,120,130]

    plt.figure(figsize=(10,6))
    plt.bar(week_labels, values)
    plt.xlabel('Week')
    plt.ylabel('Value')
    plt.title('Weekly Data')

    img = io.BytesIO()
    plt.savefig(img,format='png')
    img.seek(0)

    ratio = [0.75]

    img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')

    return render_template('manager_statistics.html', img_data=img_base64, ratio=ratio, week_labels=week_labels)

#Route: Manager Account Page
@app.route('/manager/accounts',methods=['GET','POST'])
def manager_accounts():
    accounts = User.query.all()

    return render_template("manager_accounts.html",accounts=accounts)

@app.route('/manager/accounts/<username>/<int:update_number>',methods=['GET','POST'])
def manager_accounts_update_number(username,update_number):

    account = User.query.filter_by(username=username).first()
    
    if account:
        account.priority = update_number
        db.session.commit()

        return redirect(url_for('manager_accounts'))
    else:
        return "Error", 404

@app.route('/manager/accounts/sort/low_high',methods=['GET','POST'])
def manager_accounts_sort_low_high():
    accounts = User.query.order_by(User.username).all()
    return render_template('manager_accounts.html',accounts = accounts)

@app.route('/manager/accounts/sort/high_low',methods=['GET','POST'])
def manager_accounts_sort_high_low():
    accounts = User.query.order_by(desc(User.username)).all()
    return render_template('manager_accounts.html',accounts = accounts)

@app.route('/manager/accounts/filter/<int:filter_number>',methods=['GET','POST'])
def manager_accounts_filter(filter_number):
    filtered_accounts = User.query.filter(User.priority == filter_number).all()

    if not filtered_accounts:
        filtered_accounts = []

    return render_template("manager_accounts.html",accounts = filtered_accounts) 
   

@app.route('/manager/accounts/search',methods = ['GET'])
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
def manager_listings():
    items = Item.query.all()
    return render_template("manager_listings.html",items = items)

@app.route('/manager/listings/<int:id>',methods=['GET'])
def manager_lisgings_user(id):
    user = User.query.get(id)
    user_listings = user.items
    return render_template("manager_listings_user.html", account = user, items=user_listings)   

@app.route('/manager/listings/<int:id>/<int:update_number>',methods=['GET','POST'])
def manager_listings_update_number(username,update_number):
    user_account = User.query.filter_by(id=id).first()

    if user_account:
        user_account.priority = update_number
        db.session.commit()

        return render_template("manager_listings.html",account = user_account)
    else:
        return "User not found", 404

#Route: Manager view sorting all the authentication assignments
@app.route('/manager/authentication')
def manager_auth_assignments():
    assignments = [
        {"name": "Item A", "status": "Assigned", "role": "Expert"},
        {"name": "Item B", "status": "Unassigned"},
        {"name": "Item C", "status": "Assigned", "role": "Expert"},
        {"name": "Item D", "status": "Unassigned"}
    ]
    return render_template('manager_authentication.html', assignments=assignments)


#Route: Manager's view to be able to identify experts availability
@app.route('/manager/expert_availability')
def manager_expert_availability():
    item = {

    }

    experts = [

    ]

    return render_template('manager_expert_availability.html', item=item, experts=experts)


#Route: Manager view of Items that are approved, recycled, and pending items
@app.route('/manager/overview')
def manager_overview():
    return render_template('manager_overview.html',
                           userName="",
                           userPriority="",
                           userEmail="",
                           userCategory="",
                           approved_items=[],
                           rejected_items=[],
                           pending_items=[])

# Route for Manager to Update Fees
@app.route('/manager/fees', methods=['GET', 'POST'])
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


