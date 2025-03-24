from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_socketio import SocketIO
from flask_wtf import CSRFProtect
import stripe
import os
import threading
import time

# Initialise extensions (no app bound yet)
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
migrate = Migrate()
mail = Mail()
csrf = CSRFProtect()
socketio = SocketIO(cors_allowed_origins="*", ping_interval=25, ping_timeout=60)

scheduler_running = False

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('config.Config')

    # Init extensions
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app)

    login_manager.login_view = "login"

    # Stripe
    stripe.api_key = app.config['STRIPE_SECRET_KEY']
    stripe.api_version = app.config['STRIPE_API_VERSION']

    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Register routes
    from app import routes
    app.register_blueprint(routes.bp)  # If you're using Blueprint

    # Background task: Check expired auctions
    from app.routes import check_expired_auctions
    def run_scheduler():
        global scheduler_running
        if scheduler_running:
            return
        scheduler_running = True
        while True:
            with app.app_context():
                check_expired_auctions()
            time.sleep(1)

    if not scheduler_running:
        thread = threading.Thread(target=run_scheduler, daemon=True)
        thread.start()

    return app
