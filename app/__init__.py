from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_bcrypt import Bcrypt
import os


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

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))

app.config['WTF_CSRF_ENABLED'] = False  # Disables CSRF protection


from app import routes

