# check if the user can list currently listed items

from app import app, db
from app.models import Item
import io
# import for direct file upload in testing
from werkzeug.datastructures import FileStorage
from datetime import datetime, timedelta
from flask_login import current_user

from colours import Colours


def test_view_items(loggedInClientP1):
    print(f"{Colours.YELLOW}Testing view listed items - item exists:{Colours.RESET}")

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
            expert_payment_percentage=0.15 )

        db.session.add(new_item)
        db.session.commit()

    response = loggedInClientP1.get("/user")

    assert response.status_code == 200
    #check name
    assert b'Vintage Watch' in response.data
    # check time remaining
    expected_time_remaining = expiration_time.strftime("%Y-%m-%d %H:%M")
    assert expected_time_remaining.encode() in response.data

    response = loggedInClientP1.get("/user/my_listings")

    assert response.status_code == 200
    #check name
    assert b'Vintage Watch' in response.data
    # no time check bc it went down by the time this test runs




def test_view_no_items(loggedInClientP1):
    print(f"{Colours.YELLOW}Testing view listed items - no item is added:{Colours.RESET}")

    response = loggedInClientP1.get("/user")

    assert response.status_code == 200
    assert b'No items listed' in response.data

