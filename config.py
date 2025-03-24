import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "team7")

    # DATABASE — SQLite for now, or PostgreSQL if you migrate
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///../instance/site.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # File uploads
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'images', 'items')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

    # Mail config
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "bebayteam7@gmail.com")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "your-app-password")
    MAIL_DEFAULT_SENDER = ('Bebay Team', MAIL_USERNAME)

    # Stripe
    STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "sk_test_...")
    STRIPE_API_VERSION = '2020-08-27'

    # CSRF
    WTF_CSRF_ENABLED = False  # Optional, depending on your needs
