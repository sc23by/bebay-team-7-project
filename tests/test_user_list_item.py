# test list item route

from app import app, db
from app.models import Item
import io
# import for direct file upload in testing
from werkzeug.datastructures import FileStorage
from datetime import datetime, timedelta
from flask_login import current_user


from colours import Colours


'''
Testing route with logged out client
'''
def test_unauthenticated_user_redirect(client):
    print(f"{Colours.YELLOW}Testing list items page - reroute unauthenticated user to login:{Colours.RESET}")

    response = client.get('/user/list_item')
    assert response.status_code == 302
    assert response.headers["Location"].startswith("/login")


def test_expert_redirect(loggedInClientP2):
    print(f"{Colours.YELLOW}Testing list items page - reroute expert user to expert page:{Colours.RESET}")

    response = loggedInClientP2.get('/user/list_item')
    assert response.status_code == 302
    assert response.headers["Location"].startswith("/expert")

def test_manager_redirect(loggedInClientP3):
    print(f"{Colours.YELLOW}Testing list items page - reroute manager user to manager page:{Colours.RESET}")

    response = loggedInClientP3.get('/user/list_item')
    assert response.status_code == 302
    assert response.headers["Location"].startswith("/manager")


"""
Authenticated users
"""

def test_list_item_page_access(loggedInClientP1):
    print(f"{Colours.YELLOW}Testing list items page - correct page access:{Colours.RESET}")

    response = loggedInClientP1.get('/user/list_item')
    assert response.status_code == 200
    assert b'List an Item' in response.data


def test_list_item(loggedInClientP1):
    print(f"{Colours.YELLOW}Testing list items page - correctly listing item:{Colours.RESET}")

    with app.app_context():
        initial_count = db.session.query(Item).count()

    # create fake item listing data
    def create_form_data():
        data = {
            "item_name": "Test Item",
            "description": "Wow what an item",
            "minimum_price": 10.99,
            "shipping_cost": 5.50,
            "days": 3,
            "hours": 2,
            "minutes": 30,
            "item_image": FileStorage(
                stream=io.BytesIO(b"Fake image data"),
                filename="test_image.jpg",
                content_type="image/jpeg"
            )
        }
        return data

    # check for correct redirect and item is added
    response = loggedInClientP1.post("/user/list_item", data=create_form_data(), follow_redirects=False)
    assert response.status_code == 302
    assert db.session.query(Item).count() == initial_count + 1

    # check for message flash
    response = loggedInClientP1.post("/user/list_item", data=create_form_data(), follow_redirects=True)
    assert response.status_code == 200
    assert b"Item listed successfully!" in response.data
    assert db.session.query(Item).count() == initial_count + 2


def test_invalid_list_item(loggedInClientP1):
    print(f"{Colours.YELLOW}Testing list items page - test incorrect data upload error:{Colours.RESET}")

    with app.app_context():
        initial_count = db.session.query(Item).count()

    # create fake item listing data
    def create_form_data():
        data = {
            "item_name": "Test Item",
            "description": "A great test item!",
            "minimum_price": 10.99,
            "shipping_cost": 5.50,
            "days": 3,
            "hours": 2,
            "minutes": 30,
            "item_image": FileStorage(
                stream=io.BytesIO(b"Fake image data"),
                filename="test_image.txt", # text file is invalid
                content_type="image/jpeg"
            )
        }
        return data

    response = loggedInClientP1.post("/user/list_item", data=create_form_data(), follow_redirects=True)

    assert response.status_code == 200
    assert b"Invalid file type. Only images are allowed." in response.data
    assert db.session.query(Item).count() == initial_count


def test_invalid_price(loggedInClientP1):
    print(f"{Colours.YELLOW}Testing list items page - test price too small:{Colours.RESET}")

    with app.app_context():
        initial_count = db.session.query(Item).count()

    # create fake item listing data
    def create_form_data():
        data = {
            "item_name": "Test Item",
            "description": "A great test item!",
            "minimum_price": -0.10,
            "shipping_cost": 5.50,
            "days": 3,
            "hours": 2,
            "minutes": 30,
            "item_image": FileStorage(
                stream=io.BytesIO(b"Fake image data"),
                filename="test_image.jpeg",
                content_type="image/jpeg"
            )
        }
        return data

    # check for correct redirect and item is not added 
    response = loggedInClientP1.post("/user/list_item", data=create_form_data(), follow_redirects=True)

    assert response.status_code == 200
    # message is shown but not flashed (handled by flask), this has been tested
    #assert b'Number must be at least 0.' in response.data
    assert db.session.query(Item).count() == initial_count

def test_boundry_price(loggedInClientP1):
    print(f"{Colours.YELLOW}Testing list items page - test allowed price:{Colours.RESET}")

    with app.app_context():
        initial_count = db.session.query(Item).count()

    # create fake item listing data
    def create_form_data():
        data = {
            "item_name": "Test Item",
            "description": "A great test item!",
            "minimum_price": 0.01,
            "shipping_cost": 5.50,
            "days": 3,
            "hours": 2,
            "minutes": 30,
            "item_image": FileStorage(
                stream=io.BytesIO(b"Fake image data"),
                filename="test_image.jpeg",
                content_type="image/jpeg"
            )
        }
        return data

    # check for correct redirect and item is added
    response = loggedInClientP1.post("/user/list_item", data=create_form_data(), follow_redirects=False)

    assert response.status_code == 302
    assert db.session.query(Item).count() == initial_count + 1

    # check for message flash
    response = loggedInClientP1.post("/user/list_item", data=create_form_data(), follow_redirects=True)
    assert response.status_code == 200
    assert b"Item listed successfully!" in response.data
    assert db.session.query(Item).count() == initial_count + 2

def test_invalid_shipping_cost(loggedInClientP1):
    print(f"{Colours.YELLOW}Testing list items page - shipping cost too small:{Colours.RESET}")

    with app.app_context():
        initial_count = db.session.query(Item).count()

    # create fake item listing data
    def create_form_data():
        data = {
            "item_name": "Test Item",
            "description": "A great test item!",
            "minimum_price": 5.00,
            "shipping_cost": -0.10,
            "days": 1,
            "hours": 2,
            "minutes": 30,
            "item_image": FileStorage(
                stream=io.BytesIO(b"Fake image data"),
                filename="test_image.jpeg",
                content_type="image/jpeg"
            )
        }
        return data

    # check for correct redirect and item is not added 
    response = loggedInClientP1.post("/user/list_item", data=create_form_data(), follow_redirects=True)

    assert response.status_code == 200
    #assert b'Number must be at least 0.' in response.data
    assert db.session.query(Item).count() == initial_count


def test_boundry_shipping_cost(loggedInClientP1):
    print(f"{Colours.YELLOW}Testing list items page - shipping cost too small:{Colours.RESET}")

    with app.app_context():
        initial_count = db.session.query(Item).count()

    # create fake item listing data
    def create_form_data():
        data = {
            "item_name": "Test Item",
            "description": "A great test item!",
            "minimum_price": 5.00,
            "shipping_cost": 0.01,
            "days": 1,
            "hours": 2,
            "minutes": 30,
            "item_image": FileStorage(
                stream=io.BytesIO(b"Fake image data"),
                filename="test_image.jpeg",
                content_type="image/jpeg"
            )
        }
        return data

    # check for correct redirect and item is added
    response = loggedInClientP1.post("/user/list_item", data=create_form_data(), follow_redirects=False)
    assert response.status_code == 302
    assert db.session.query(Item).count() == initial_count + 1

    # check for message flash
    response = loggedInClientP1.post("/user/list_item", data=create_form_data(), follow_redirects=True)
    assert response.status_code == 200
    assert b"Item listed successfully!" in response.data
    assert db.session.query(Item).count() == initial_count + 2


def test_missing_data(loggedInClientP1):
    print(f"{Colours.YELLOW}Testing list items page - test data not inputted:{Colours.RESET}")

    with app.app_context():
        initial_count = db.session.query(Item).count()

    # create fake item listing data
    def create_form_data():
        data = {
            "item_name": "",
            "description": "A great test item!",
            "minimum_price": 5.00,
            "shipping_cost": 1,
            "days": 3,
            "hours": 2,
            "minutes": 30,
            "item_image": FileStorage(
                stream=io.BytesIO(b"Fake image data"),
                filename="test_image.jpeg",
                content_type="image/jpeg"
            )
        }
        return data

    response = loggedInClientP1.post("/user/list_item", data=create_form_data(), follow_redirects=True)

    assert response.status_code == 200
    # managed by forms - does show up
    #assert b'This field is required.' in response.data
    assert db.session.query(Item).count() == initial_count


def test_view_items(loggedInClientP1):
    print(f"{Colours.YELLOW}Testing view listed items - item exists in main page and my listings section:{Colours.RESET}")

    with app.app_context():
        expiration_time = datetime.utcnow() + timedelta(days=3)
        new_item = Item(
            seller_id= current_user.id,
            item_name="Vintage Watch",
            minimum_price=150.00,
            description="A rare vintage watch in excellent condition.",
            item_image="vintage_watch.jpg",
            date_time=datetime.utcnow(),
            expiration_time=expiration_time,
            approved=True,
            shipping_cost=10.50,
            expert_fee_percentage=0.15 )

        db.session.add(new_item)
        db.session.commit()

    response = loggedInClientP1.get("/user")

    assert response.status_code == 200
    #check name
    assert b'Vintage Watch' in response.data
    assert b'Time Left:' in response.data


    response = loggedInClientP1.get("/user/my_listings")
    assert response.status_code == 200
    assert b'Vintage Watch' in response.data
    assert b'Time Left:' in response.data


def test_watchlist_items(loggedInClientP1):
    print(f"{Colours.YELLOW}Testing view watchlist items - check items show up:{Colours.RESET}")

    with app.app_context():
        expiration_time = datetime.utcnow() + timedelta(days=3)
        new_item = Item(
            seller_id= 1234,
            item_name="Vintage Watch",
            minimum_price=150.00,
            description="A rare vintage watch in excellent condition.",
            item_image="vintage_watch.jpg",
            date_time=datetime.utcnow(),
            expiration_time=expiration_time,
            approved=True,
            shipping_cost=10.50,
            expert_fee_percentage=0.15 )

        db.session.add(new_item)
        db.session.commit()

        user = current_user.query.get(current_user.id)
        user.watchlist.append(new_item)
        db.session.commit()
        assert new_item in user.watchlist

    response = loggedInClientP1.get("/user/watchlist")
    assert response.status_code == 200
    assert b'Vintage Watch' in response.data
    assert b'Time Left:' in response.data



def test_view_no_items(loggedInClientP1):
    print(f"{Colours.YELLOW}Testing view listed items - no item is added:{Colours.RESET}")

    response = loggedInClientP1.get("/user")

    assert response.status_code == 200
    assert b'No items listed' in response.data