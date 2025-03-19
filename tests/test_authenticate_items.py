# test users are able to request items authenticated and experts are able to review them

from app import app, db,bcrypt
from app.models import WaitingList, Item, User, ExpertAvailabilities
from datetime import datetime, timedelta
from flask_login import current_user
import io
from werkzeug.datastructures import FileStorage

from colours import Colours


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
        ),
        "authenticate": True
    }
    return data

def test_request_authentication(loggedInClientP1):
    print(f"{Colours.YELLOW}Testing authenticate items - users can request authentication and items added to waitlist:{Colours.RESET}")

    response = loggedInClientP1.post("/user/list_item", data=create_form_data())
    assert response.status_code ==  302
    
    with app.app_context():
        item = Item.query.filter_by(item_name="Test Item").first()
        assert item is not None

        waitlist_entry = WaitingList.query.filter_by(item_id=item.item_id).first()
        assert waitlist_entry is not None

        assert waitlist_entry.request_time is not None
        expected_expire_time = waitlist_entry.request_time + timedelta(days=2)
        # let for some variation in seconds
        assert abs((waitlist_entry.expire_time - expected_expire_time).total_seconds()) < 5


def test_manager_sees_request(loggedInClientP3):
    print(f"{Colours.YELLOW}Testing authenticate items - mamager can see the request needs to be assigned to an expert:{Colours.RESET}")

    with app.app_context():
        item = Item(
            item_id= 1,
            seller_id=1,
            item_name="apel",
            description="Wow what an item",
            minimum_price=10.99,
            shipping_cost=5.50,
            days=3,
            hours=2,
            minutes=30,
            item_image="test_image.jpg",
            date_time=None, # not authenticated yet
            expiration_time=None, # not authenticated yet
            approved=False,
            expert_payment_percentage=10.0,
            site_fee_percentage=1.0,
            expert_fee_percentage=4.0,
            sold=False)
        
        db.session.add(item)
        db.session.commit()

        waiting_list_entry = WaitingList(item_id=item.item_id)
        db.session.add(waiting_list_entry)
        db.session.commit()
        
    response = loggedInClientP3.get("/manager/expert_availability")
    assert b"apel" in response.data

def test_manager_assign_expert(loggedInClientP3):
    print(f"{Colours.YELLOW}Testing authenticate items - manager can assign expert:{Colours.RESET}")

    with app.app_context():
        # an espert to assign to
        expert = User(id = 10,
                        username='expert',
                        email='expert@example.com',
                        password=bcrypt.generate_password_hash('password'),
                        first_name='Test2', 
                        last_name='User', 
                        priority=2)
        db.session.add(expert)
        db.session.commit()


        # some avalable entries
        splitDates = ['2025-03-20', '2025-03-21']
        splitStartTimes = ['10:00', '14:00']

        for date, start_time in zip(splitDates, splitStartTimes):
            date_obj = datetime.strptime(date, '%Y-%m-%d').date()
            start_time_obj = datetime.strptime(start_time, '%H:%M').time()

            availability = ExpertAvailabilities(
                user_id=expert.id,
                date=date_obj,
                start_time=start_time_obj,
                duration=1
            )
            db.session.add(availability)
        db.session.commit()

        # an item to assign
        item = Item(
            item_id = 1,
            seller_id=1,
            item_name="apel",
            description="Wow what an item",
            minimum_price=10.99,
            shipping_cost=5.50,
            days=3,
            hours=2,
            minutes=30,
            item_image="test_image.jpg",
            date_time=None, # not authenticated yet
            expiration_time=None, # not authenticated yet
            approved=False,
            expert_payment_percentage=10.0,
            site_fee_percentage=1.0,
            expert_fee_percentage=4.0,
            sold=False)
        
        db.session.add(item)
        db.session.commit()

        waiting_list_entry = WaitingList(item_id=item.item_id)
        db.session.add(waiting_list_entry)
        db.session.commit()
            
    response = loggedInClientP3.post("/assign_expert", data = {
        'item_id': 1,
        'selected_expert': 10,
        'selected_time': 1,
        'expert_payment_percentage': 50})
    
    assert response.status_code == 302

    with app.app_context():
        expert = User.query.get(10)
        item = Item.query.filter_by(item_id=1).first()
        assert item.expert == expert


def test_expert_vue_assignment(loggedInClientP2):
    print(f"{Colours.YELLOW}Testing authenticate items - expert can see item assigned to them:{Colours.RESET}")

    with app.app_context():
        item = Item(
            item_id = 1,
            seller_id=1,
            item_name="apel",
            description="Wow what an item",
            minimum_price=10.99,
            shipping_cost=5.50,
            days=3,
            hours=2,
            minutes=30,
            item_image="test_image.jpg",
            date_time=None, # not authenticated yet
            expiration_time=None, # not authenticated yet
            approved=False,
            expert_payment_percentage=10.0,
            site_fee_percentage=1.0,
            expert_fee_percentage=4.0,
            sold=False,
            expert = current_user)
        
        db.session.add(item)
        db.session.commit()

        waiting_list_entry = WaitingList(item_id=item.item_id)
        db.session.add(waiting_list_entry)
        db.session.commit()
            
    response = loggedInClientP2.get("/expert/assignments")
    assert response.status_code == 200
    assert b"apel" in response.data


def test_expert_aprove(loggedInClientP2):
    print(f"{Colours.YELLOW}Testing authenticate items - expert can aprove items:{Colours.RESET}")

    with app.app_context():
        item = Item(
            item_id = 1,
            seller_id=1,
            item_name="apel",
            description="Wow what an item",
            minimum_price=10.99,
            shipping_cost=5.50,
            days=3,
            hours=2,
            minutes=30,
            item_image="test_image.jpg",
            date_time=None, # not authenticated yet
            expiration_time=None, # not authenticated yet
            approved=False,
            expert_payment_percentage=10.0,
            site_fee_percentage=1.0,
            expert_fee_percentage=4.0,
            sold=False,
            expert = current_user)
        
        db.session.add(item)
        db.session.commit()

        waiting_list_entry = WaitingList(item_id=item.item_id)
        db.session.add(waiting_list_entry)
        db.session.commit()
            
    response = loggedInClientP2.post("/expert/approve_item/1")
    assert response.status_code == 302

    with app.app_context():
        waiting_list_item = WaitingList.query.filter_by(item_id=1).first()
        assert waiting_list_item is None