from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO
import os
import stripe
# For checking expired auctions
import time
import threading

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'team7'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

# File upload settings
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'images')
ITEM_IMAGE_FOLDER = os.path.join(UPLOAD_FOLDER, 'items')
# PROFILE_IMAGE_FOLDER = os.path.join(UPLOAD_FOLDER, 'profiles')

# Ensure upload folders exist
os.makedirs(ITEM_IMAGE_FOLDER, exist_ok=True)
# os.makedirs(PROFILE_IMAGE_FOLDER, exist_ok=True)

app.config['ITEM_IMAGE_FOLDER'] = ITEM_IMAGE_FOLDER
# app.config['PROFILE_IMAGE_FOLDER'] = PROFILE_IMAGE_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Add to Flask app config
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

# Add Bebay email
from flask_mail import Mail

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'bebayteam7@gmail.com'
app.config['MAIL_PASSWORD'] = 'yxhn ipdi otrs dwip'
app.config['MAIL_DEFAULT_SENDER'] = ('Bebay Team', 'bebayteam7@gmail.com')

mail = Mail(app)

# Initialize extensions:
# Database
db = SQLAlchemy(app)

# Login
login_manager = LoginManager(app)
login_manager.login_view = "login"

# Migrations
migrate = Migrate(app, db) 

# Encyrption
bcrypt = Bcrypt(app)

# Enable CSRF Protection
csrf = CSRFProtect(app)

# Websockets
socketio = SocketIO(app, ping_interval=25, ping_timeout=60, max_http_buffer_size=1024)

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))

 # Disables CSRF protection
app.config['WTF_CSRF_ENABLED'] = False 

# Loading configuration from config.py
app.config.from_object('config')

# Correct way to set Stripe API key
stripe.api_key = app.config['STRIPE_SECRET_KEY']
stripe.api_version = '2020-08-27'  # 👈 Add this

from app import routes
from app.routes import check_expired_auctions

scheduler_running = False  
# Background Task: Periodically Check for Expired Auctions
def run_scheduler():
    from datetime import datetime
    from app.routes import check_expired_auctions
    global scheduler_running

    if scheduler_running:
        return  # Avoid starting multiple threads

    scheduler_running = True
    #print("Scheduler thread started.")

    while True:
        with app.app_context():
            check_expired_auctions()
        #print(f"Active threads:{threading.enumerate()}\n")
        time.sleep(1)



# Start the background thread
if not scheduler_running:
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()


# threads are being continuously created and destroyed, this is taxing for the system maybe we can implement thread pool?