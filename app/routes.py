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
            return redirectBasedOnPriority(current_user)  # Redirect based on user priority
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
        if current_user.priority != 1:  # If not an expert
            flash("You don't have user permissions to access this page.", "danger")
            return redirectBasedOnPriority(current_user)
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
        if current_user.priority != 2:  # If not an expert
            flash("You don't have expert permissions to access this page.", "danger")
            return redirectBasedOnPriority(current_user)
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
        if current_user.priority != 3:  # If not a manager
            flash("You don't have manager permissions to access this page.", "danger")
            return redirectBasedOnPriority(current_user)
        return f(*args, **kwargs)
    return decorated_function


# Functions

# Function: Redirect based on priority
def redirectBasedOnPriority(user):
    """
    Function to redirect user to correct page based on their priority.
    """
    if user.priority == 3:  # Manager
        return redirect(url_for('managerHome'))
    elif user.priority == 2:  # Expert
        return redirect(url_for('expertHome'))
    elif user.priority == 1:  # Normal User
        return redirect(url_for('loggedIn'))
    else:  # Guest
        return redirect(url_for('mainPage'))


# Guest Pages

# Route: Login Page
@app.route('/')
@guest_required
def mainPage():
    """
    Redirects to main page when website first opened.
    """
    if current_user.is_authenticated:
        return redirect(redirectBasedOnPriority)
    return render_template('mainPage.html')


# Route: Registration Page    
@app.route('/register', methods=['GET', 'POST'])
@guest_required
def register():
    """
    Handle user registration.
    """
    form = RegistrationForm()

    if current_user.is_authenticated:
        return redirect(redirectBasedOnPriority)

    if form.validate_on_submit():

        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('register'))

        if User.query.filter_by(email=form.email.data).first():
            flash('Email already exists. Please choose a different one.', 'danger')
            return redirect(url_for('register'))

        hashed_password = bcrypt.generate_password_hash(form.password.data)
        user = User(firstName=form.firstName.data, lastName=form.lastName.data, username=form.username.data, email=form.email.data, password=hashed_password)
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
        return redirectBasedOnPriority(user)
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirectBasedOnPriority(user)
        flash('Invalid username or password.', 'danger')
    return render_template('login.html', form=form)

# Route: Logout
@app.route('/logout')
@login_required
def logout():
    """
    Log the user out and redirect to the mainPage page.
    """
    logout_user()
    return redirect(url_for('mainPage'))


# User Pages

# Route: Logged In Page
@app.route('/loggedIn')
@user_required
def loggedIn():
    """
    Redirects to main page when website first opened.
    """
    return render_template('loggedIn.html')

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
        elif form.myListings.data:
            return redirect(url_for("myListings"))
        elif form.watchlist.data:
            return redirect(url_for("watchlist"))
        elif form.notifications.data:
            return redirect(url_for("notifications"))

    return render_template('account.html', form=form)

# Route: My Listings
@app.route('/myListings', methods=['GET', 'POST'])
@user_required
def myListings():
    """
    Redirects to my listings page, has buttons to other pages.
    """
    form = SideBarForm()

    if form.validate_on_submit():
        if form.info.data:
            return redirect(url_for("account"))
        elif form.myListings.data:
            return redirect(url_for("myListings"))
        elif form.watchlist.data:
            return redirect(url_for("watchlist"))
        elif form.notifications.data:
            return redirect(url_for("notifications"))

    return render_template('myListings.html', form=form)

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
        elif form.myListings.data:
            return redirect(url_for("myListings"))
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
        elif form.myListings.data:
            return redirect(url_for("myListings"))
        elif form.watchlist.data:
            return redirect(url_for("watchlist"))
        elif form.notifications.data:
            return redirect(url_for("notifications"))

    return render_template('notifications.html', form=form)


# Expert Pages

# Route: Experts Home Page
@app.route('/expertsHome')
@expert_required
def expertHome():
    """
    Redirects to experts home page when website first opened.
    """
    return render_template('expertsHome.html')

#Route: Expert Assignments Page
@app.route('/expertAssignments')
@expert_required
def expertAssignments():
    return render_template('expertAssignments.html')

#Route: Expert Authentication Page
@app.route('/itemAuthentication')
@expert_required
def itemAuthentication():
    return render_template('itemAuthentication.html')

#Route: Expert Messaging Page
@app.route('/expertsMessaging')
@expert_required
def expertsMessaging():
    return render_template('expertsMessaging.html')

#Route: Expert Avaliablity Page
@app.route('/setAvailability')
@expert_required
def setAvailability():
    return render_template('setAvailability.html')


# Manager Pages

# Route: Managers Home
@app.route('/managerHome')
@manager_required
def managerHome():
    """
    Redirects to managers home page when website first opened.
    """
    return render_template('managerHome.html')

#Route: Manager Stats Page
@app.route('/manager', methods=['GET','POST'])
@manager_required
def manager():
    return render_template("managerStats.html")

#Route: Manager Account Page
@app.route('/manageracc',methods=['GET','POST'])
@manager_required
def manageracc():
    return render_template("managerAccounts.html")

#Route: Manager Listing Page
@app.route('/managerlistings',methods=['GET','POST'])
@manager_required
def managerlist():
    return render_template("managerListings.html")