from app import app, db, bcrypt
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, current_user, login_required,logout_user
from app.forms import RegistrationForm, LoginForm, SideBarForm
from app.models import User
from functools import wraps


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
        return redirect(url_for('expert_home'))
    elif user.priority == 1:  # Normal User
        return redirect(url_for('user_home'))
    else:  # Guest
        return redirect(url_for('guest_home'))


# Guest Pages

# Route: Login Page
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
@app.route('/user_home')
@user_required
def user_home():
    """
    Redirects to main page when website first opened.
    """
    return render_template('user_home.html')

# Route: Account
@app.route('/account', methods=['GET', 'POST'])
@user_required
def account():
    """
    Redirects to account page, has buttons to other pages.
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

    return render_template('account.html', form=form)

# Route: My Listings
@app.route('/my_listings', methods=['GET', 'POST'])
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

    return render_template('my_listings.html', form=form)

# Route: Watchlist
@app.route('/watchlist', methods=['GET', 'POST'])
@user_required
def watchlist():
    """
    Redirects to watchlist page, has buttons to other pages.
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

    return render_template('watchlist.html', form=form)

# Route: Notifications
@app.route('/notifications', methods=['GET', 'POST'])
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

    return render_template('notifications.html', form=form)


# Expert Pages

# Route: Experts Home Page
@app.route('/expert_home')
@expert_required
def expert_home():
    """
    Redirects to experts home page when website first opened.
    """
    return render_template('expert_home.html')

#Route: Expert Assignments Page
@app.route('/expert_assignments')
@expert_required
def expert_assignments():
    return render_template('expert_assignments.html')

#Route: Expert Authentication Page
@app.route('/item_authentication')
@expert_required
def item_authentication():
    return render_template('item_authentication.html')

#Route: Expert Messaging Page
@app.route('/expert_messaging')
@expert_required
def expert_messaging():
    return render_template('expert_messaging.html')

#Route: Expert Avaliablity Page
@app.route('/set_availability')
@expert_required
def set_availability():
    return render_template('set_availability.html')


# Manager Pages

# Route: Managers Home
# Remove
@app.route('/manager_home')
@manager_required
def manager_home():
    """
    Redirects to managers home page when website first opened.
    """
    return render_template('manager_home.html')


#Route: Manager Stats Page
@app.route('/manager_stats', methods=['GET','POST'])
@manager_required
def manager_stats():
    return render_template("manager_stats.html")

#Route: Manager Account Page
@app.route('/manager_accounts',methods=['GET','POST'])
@manager_required
def manager_accounts():
    return render_template("manager_accounts.html")

#Route: Manager Listing Page
@app.route('/manager_listings',methods=['GET','POST'])
@manager_required
def manager_listings():
    return render_template("manager_listings.html")