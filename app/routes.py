from app import app, db, bcrypt
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, current_user, login_required,logout_user
from app.forms import RegistrationForm, LoginForm, SideBarForm, UserInfoForm, ChangePasswordForm, CardInfoForm
from app.models import User

# Route: Login Page
@app.route('/')
def mainPage():
    """
    Redirects to main page when website first opened.
    """
    if current_user.is_authenticated:
        return redirectBasedOnPriority(current_user)
    return render_template('mainPage.html')

# Route: Registration Page    
@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handle user registration.
    """
    form = RegistrationForm()

    if current_user.is_authenticated:
        return redirectBasedOnPriority(current_user)

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

# Function: Redirect based on priority
def redirectBasedOnPriority(user):
    """
    Function to redirect user to correct page based on their priority.
    """
    if user.priority == 3:  # Manager
        return redirect(url_for('managerHome'))
    elif user.priority == 2:  # Expert
        return redirect(url_for('expertHome'))
    else:  # Normal User
        return redirect(url_for('loggedIn'))

# Route: Managers Home
@app.route('/managerHome')
@login_required
def managerHome():
    """
    Redirects to managers home page when website first opened.
    """
    return render_template('managerHome.html')

# Route: Experts Home Page
@app.route('/expertsHome')
@login_required
def expertHome():
    """
    Redirects to experts home page when website first opened.
    """
    return render_template('expertsHome.html')

# Route: Logout
@app.route('/logout')
def logout():
    """
    Log the user out and redirect to the mainPage page.
    """
    logout_user()
    return redirect(url_for('mainPage'))
    
@login_required
def logout():
    """
    Log the user out and redirect to the mainPage page.
    """
    logout_user()
    return redirect(url_for('mainPage'))

# Route: Logged In Page
@app.route('/loggedIn')
@login_required
def loggedIn():
    """
    Redirects to main page when website first opened.
    """
    return render_template('loggedIn.html')

# Route: Account
@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    """
    Redirects to account page, has buttons to other pages and user information.
    """
    sidebar_form = SideBarForm()

    if sidebar_form.validate_on_submit() and 'sidebar' in request.form:
        if sidebar_form.info.data:
            return redirect(url_for("account"))
        elif sidebar_form.myListings.data:
            return redirect(url_for("myListings"))
        elif sidebar_form.watchlist.data:
            return redirect(url_for("watchlist"))
        elif sidebar_form.notifications.data:
            return redirect(url_for("notifications"))
        elif sidebar_form.logout.data:
            return redirect(url_for("logout")) 

    info_form = UserInfoForm()

    if info_form.validate_on_submit():
        return redirect(url_for('account'))

    password_form = ChangePasswordForm()

    if password_form.validate_on_submit():
        return redirect(url_for('account'))

    card_form = CardInfoForm()

    if card_form.validate_on_submit():
        return redirect(url_for('account'))

    return render_template('account.html', sidebar_form=sidebar_form, info_form=info_form, password_form=password_form, card_form=card_form)

# Route: My Listings
@app.route('/myListings', methods=['GET', 'POST'])
@login_required
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
        elif form.logout.data:
            return redirect(url_for("logout"))

    return render_template('myListings.html', form=form)

# Route: Watchlist
@app.route('/watchlist', methods=['GET', 'POST'])
@login_required
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
        elif form.logout.data:
            return redirect(url_for("logout"))

    return render_template('watchlist.html', form=form)

# Route: Notifications
@app.route('/notifications', methods=['GET', 'POST'])
@login_required
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
        elif form.logout.data:
            return redirect(url_for("logout"))

    return render_template('notifications.html', form=form)

@app.route('/expertAssignments')
def expertAssignments():
    return render_template('expertAssignments.html')

@app.route('/itemAuthentication')
def itemAuthentication():
    return render_template('itemAuthentication.html')

@app.route('/expertsMessaging')
def expertsMessaging():
    return render_template('expertsMessaging.html')

@app.route('/setAvailability')
def setAvailability():
    return render_template('setAvailability.html')

#Route: Manager Page
@app.route('/manager', methods=['GET','POST'])
def manager():
    return render_template("managerStats.html")

@app.route('/manageracc',methods=['GET','POST'])
def manageracc():
    return render_template("managerAccounts.html")

@app.route('/managerlistings',methods=['GET','POST'])
def managerlist():
    return render_template("managerListings.html")