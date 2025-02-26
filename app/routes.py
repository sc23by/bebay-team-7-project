from app import app, db, bcrypt
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, current_user, login_required,logout_user
from app.forms import RegistrationForm, LoginForm, SideBarForm
from app.models import User


# Route: Login Page
@app.route('/')
def mainPage():
    """
    Redirects to main page when website first opened.
    """
    return render_template('mainPage.html')

# Route: Registration Page    
@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handle user registration.
    """
    form = RegistrationForm()

    if current_user.is_authenticated:
        return redirect(url_for('loggedIn'))

    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('register'))

        if User.query.filter_by(email=form.email.data).first():
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('register'))

        hashed_password = bcrypt.generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
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
        return redirect(url_for('loggedIn'))
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('loggedIn'))
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

@app.route('/loggedIn')
@login_required
def loggedIn():
    """
    Redirects to main page when website first opened.
    """
    return render_template('loggedIn.html')

@app.route('/account', methods=['GET', 'POST'])
def account():

    form = SideBarForm()

    if form.validate_on_submit():
        if form.info.data:
            return redirect(url_for("account"))
        elif form.listings.data:
            return redirect(url_for("listings"))
        elif form.watchlist.data:
            return redirect(url_for("watchlist"))
        elif form.notifications.data:
            return redirect(url_for("notifications"))

    return render_template('account.html', form=form)

@app.route('/listings', methods=['GET', 'POST'])
def listings():

    form = SideBarForm()

    if form.validate_on_submit():
        if form.info.data:
            return redirect(url_for("account"))
        elif form.listings.data:
            return redirect(url_for("listings"))
        elif form.watchlist.data:
            return redirect(url_for("watchlist"))
        elif form.notifications.data:
            return redirect(url_for("notifications"))

    return render_template('myListings.html', form=form)

@app.route('/watchlist', methods=['GET', 'POST'])
def watchlist():

    form = SideBarForm()

    if form.validate_on_submit():
        if form.info.data:
            return redirect(url_for("account"))
        elif form.listings.data:
            return redirect(url_for("listings"))
        elif form.watchlist.data:
            return redirect(url_for("watchlist"))
        elif form.notifications.data:
            return redirect(url_for("notifications"))

    return render_template('watchlist.html', form=form)

@app.route('/notifications', methods=['GET', 'POST'])
def notifications():

    form = SideBarForm()

    if form.validate_on_submit():
        if form.info.data:
            return redirect(url_for("account"))
        elif form.listings.data:
            return redirect(url_for("listings"))
        elif form.watchlist.data:
            return redirect(url_for("watchlist"))
        elif form.notifications.data:
            return redirect(url_for("notifications"))

    return render_template('notifications.html', form=form)

#Route: Manager Page
@app.route('/manager', methods=['GET','POST'])
def manager():
    return render_template("managerStats.html")