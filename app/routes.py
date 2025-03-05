from app import app, db, bcrypt
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, current_user, login_required,logout_user
from app.forms import RegistrationForm, LoginForm, SideBarForm, UserInfoForm, ChangePasswordForm, CardInfoForm, ListItemForm
from app.models import User, Item
from functools import wraps
import matplotlib.pyplot as plt
import io
import base64
from werkzeug.utils import secure_filename
import os
import uuid

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
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


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
@app.route('/user')
@user_required
def user_home():
    """
    Redirects to main page when website first opened. Displays all items.
    """
    items = Item.query.all()  # Fetch all items from the database
    return render_template('user_home.html', items = items)

# Route: Account
@app.route('/user/account', methods=['GET', 'POST'])
@login_required
def account():
    """
    Redirects to account page, has buttons to other pages and user information.
    """
    sidebar_form = SideBarForm()

    if sidebar_form.validate_on_submit() and 'sidebar' in request.form:
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

    if info_form.validate_on_submit():
        return redirect(url_for('account'))

    password_form = ChangePasswordForm()

    if password_form.validate_on_submit():
        return redirect(url_for('account'))

    card_form = CardInfoForm()

    if card_form.validate_on_submit():
        return redirect(url_for('account'))

    return render_template('user_account.html', sidebar_form=sidebar_form, info_form=info_form, password_form=password_form, card_form=card_form)

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

    return render_template('user_my_listings.html', form=form)

# Route: Watchlist
@app.route('/user/watchlist', methods=['GET', 'POST'])
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
        elif form.logout.data:
            return redirect(url_for("logout"))

    return render_template('user_watchlist.html', form=form)

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

    return render_template('user_notifications.html', form=form)

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

        # Store filename in DB (relative path)
        new_item = Item(
            seller_id=current_user.id,
            item_name=form.item_name.data,
            description=form.description.data,
            minimum_price=form.minimum_price.data,
            item_image=filename,  # Store filename only
            duration=form.duration.data,
            time=form.time.data,
            date=form.date.data,
            shipping_cost=form.shipping_cost.data,
            approved=False
        )
        
        db.session.add(new_item)
        db.session.commit()
        flash('Item listed successfully!', 'success')
        return redirect(url_for('user_home')) 
    else:
        flash('Invalid file type. Only images are allowed.', 'danger')
    return render_template('user_list_item.html', form=form)


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
@app.route('/expert/availability')
@expert_required
def expert_set_availability():
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
def manager_stats():
    ratio = [34,32,16,20]
    labels = ['Generated income','Customer cost','Postal cost','Experts cost']
    colors=['red','green','blue','orange']

    plt.pie(ratio, labels=labels,colors=colors,autopct=lambda p: f'{p:.1f}%\n £ {p * sum(ratio) / 100:.0f}')
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    img_base64 = base64.b64encode(img.getvalue()).decode()

    return render_template('manager_statistics.html',img_data=img_base64,ratio=ratio,labels=labels)

accounts = [
        {"username": "Jonghyun","number": 1},
        {"username": "Feibi","number": 2},
        {"username": "Bellaly","number": 1},
        {"username": "Rammy","number": 1},
        {"username": "MM","number": 3},
        {"username": "Leyna","number": 1}
    ]


#Route: Manager Account Page
@app.route('/manager/accounts',methods=['GET','POST'])
def manager_accounts():
    return render_template("manager_accounts.html",accounts=accounts)

@app.route('/manager/accounts/<username>/<int:update_number>',methods=['GET','POST'])
def manager_accounts_update_number(username,update_number):
    for account in accounts:
        if account['username'] == username:
            account['number'] = update_number
            break

    return redirect(url_for('manager_accounts'))

@app.route('/manager/accounts/sort/low_high',methods=['GET','POST'])
def manager_accounts_sort_low_high():
    accounts.sort(key = lambda x: x['username'])
    return redirect(url_for('manager_accounts'))



#Route: Manager Listing Page
@app.route('/manager/listings',methods=['GET','POST'])
@manager_required
def manager_listings():
    listings = [
        {"title": "Jumper","image" : "https://image.hm.com/assets/006/35/ee/35eeb535903be97df8fcfd77b21822b91862ba2c.jpg?imwidth=1260"},
        {"title": "Pants","image" : "https://image.hm.com/assets/hm/7a/9e/7a9e28408cddce6247b5173b6a54b9a13b98dc1c.jpg?imwidth=1260"}

    ]
    return render_template("manager_listings.html",listings=listings)


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
        "name": "Item A",
        "assigned_expert": "John Doe",
        "description": "This item requires authentication by an expert."
    }

    experts = [
        {"name": "Alice Smith", "available": "Now"},
        {"name": "Bob Johnson", "available": "48h"},
        {"name": "Charlie Davis", "available": "Now"},
        {"name": "Diana Lee", "available": "48h"}
    ]

    return render_template('manager_expert_availability.html', item=item, experts=experts)



#Route: Manager view of Items that are approved, recycled, and pending items
@app.route('/manager_overview')
def manager_dashboard():
    return render_template('manager/overview).html',
                           userName="JohnDoe",
                           userPriority=2,
                           userEmail="john.doe@example.com",
                           userCategory="Electronics",
                           approved_items=[{"name": "Laptop"}, {"name": "Smartphone"}, {"name": "Headphones"}],
                           rejected_items=[{"name": "Old Monitor"}, {"name": "Broken Keyboard"}],
                           pending_items=[{"name": "Gaming Console"}, {"name": "Tablet"}])
