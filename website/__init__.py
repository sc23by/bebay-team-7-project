from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

Initialize extensions
db = SQLAlchemy(website)

login_manager = LoginManager(website)
login_manager.login_view = "login"

migrate = Migrate(website, db) 

# put user loader here

Import routes
from website import routes

Enable CSRF Protection
csrf = CSRFProtect(website)