from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_bcrypt import Bcrypt

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'team7'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

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

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))

# Import routes
from app import routes

# Enable CSRF Protection
csrf = CSRFProtect(app)
