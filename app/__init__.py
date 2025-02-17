from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'team7'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
migrate = Migrate(app, db) 

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return none

# Import routes
from app import routes

# Enable CSRF Protection
csrf = CSRFProtect(app)
