# test if the manager can view site stats and edit site fee percentages

from app import app, db, bcrypt
from app.models import User, Item, SoldItem
from colours import Colours

def test_manager_weekly_cost(loggedInClientP3, populate_database):
    with app.app_context():
        
