# route test setup - discovered by all route tests
# creats clients and other fixtures
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db, bcrypt
from app.models import User,SoldItem,Item
from datetime import datetime
import pytest


'''
Creating fixtures to test routes with
client: unlogged in client
loggedInClient: client who has logged in
'''
@pytest.fixture
def client():
    print("\nSetting up the test client")
    
    # testing mode enabled, use memory db not the real one, dissable security
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        with app.app_context():
            # create temp db
            db.create_all()
        yield client
        with app.app_context():
            # post test cleanup
            db.drop_all()
    print("\nTearing down the test client")

@pytest.fixture
def loggedInClientP1(client):
    with app.app_context():
        test_user = User(username='testuser1',
                         email='test1@example.com',
                         password=bcrypt.generate_password_hash('password'),
                         first_name='Test', 
                         last_name='User', 
                         priority=1)
        db.session.add(test_user)
        db.session.commit()

    # log in the user
    response = client.post('/login', data={
        'username': 'testuser1',
        'password': 'password'
    }, follow_redirects=True)

    assert response.status_code == 200
    yield client

@pytest.fixture
def loggedInClientP2(client):
    with app.app_context():
        test_user = User(username='testuser2',
                         email='test2@example.com',
                         password=bcrypt.generate_password_hash('password'),
                         first_name='Test2', 
                         last_name='User', 
                         priority=2,
                         expertise='other')
        db.session.add(test_user)
        db.session.commit()

    # log in the user
    response = client.post('/login', data={
        'username': 'testuser2',
        'password': 'password'
    }, follow_redirects=True)

    assert response.status_code == 200
    yield client

@pytest.fixture
def loggedInClientP3(client):
    with app.app_context():
        test_user = User(username='testuser3',
                         email='test3@example.com',
                         password=bcrypt.generate_password_hash('password'),
                         first_name='Test3', 
                         last_name='User', 
                         priority=3)
        db.session.add(test_user)
        db.session.commit()

    # log in the user
    response = client.post('/login', data={
        'username': 'testuser3',
        'password': 'password'
    }, follow_redirects=True)

    assert response.status_code == 200
    yield client


@pytest.fixture
def populate_database():
    """Fixture to populate the database before tests."""
    with app.app_context():
        # Clear database
        db.session.query(SoldItem).delete()
        db.session.query(Item).delete()
        db.session.query(User).delete()
        db.session.commit()

        # Create users
        seller = User(
            username='seller',
            email='seller@example.com',
            password=bcrypt.generate_password_hash('password'),
            first_name='Seller',
            last_name='Lastname'
        )
        buyer = User(
            username='buyer',
            email='buyer@example.com',
            password=bcrypt.generate_password_hash('password'),
            first_name='Buyer',
            last_name='Lastname'
        )
        db.session.add_all([seller, buyer])
        db.session.commit()

        # Add test items
        items = [
            Item(
                seller_id=seller.id,
                item_name="apel1",
                description="Wow what an item",
                minimum_price=10.99,
                shipping_cost=5.50,
                days=3,
                hours=2,
                minutes=30,
                item_image="test_image.jpg",
                date_time=datetime(2025, 3, 21, 13, 30, 8, 586181),
                expiration_time=datetime(2025, 3, 21, 13, 10, 0, 0),
                approved=False,
                site_fee_percentage=1.0,
                expert_fee_percentage=4.0,
                sold=True
            ),
            Item(
                seller_id=seller.id,
                item_name="apel2",
                description="Wow what an item",
                minimum_price=10.99,
                shipping_cost=5.50,
                days=3,
                hours=2,
                minutes=30,
                item_image="test_image.jpg",
                date_time=datetime(2025, 3, 21, 13, 30, 8, 586181),
                expiration_time=datetime(2025, 3, 21, 13, 10, 0, 0),
                approved=False,
                site_fee_percentage=2.0,
                expert_fee_percentage=2.0,
                sold=True
            ),
            Item(
                seller_id=seller.id,
                item_name="apel3",
                description="Wow what an item",
                minimum_price=10.99,
                shipping_cost=5.50,
                days=3,
                hours=2,
                minutes=30,
                item_image="test_image.jpg",
                date_time=datetime(2025, 3, 21, 13, 30, 8, 586181),
                expiration_time=datetime(2025, 3, 21, 13, 10, 0, 0),
                approved=False,
                site_fee_percentage=1.0,
                expert_fee_percentage=3.0,
                sold=True
            ),
            Item(
                seller_id=seller.id,
                item_name="apel4",
                description="Wow what an item",
                minimum_price=10.99,
                shipping_cost=5.50,
                days=3,
                hours=2,
                minutes=30,
                item_image="test_image.jpg",
                date_time=datetime(2025, 3, 21, 13, 30, 8, 586181),
                expiration_time=datetime(2025, 3, 21, 13, 10, 0, 0),
                approved=False,
                site_fee_percentage=1.0,
                expert_fee_percentage=9.0,
                sold=True
            ),
        ]

        db.session.add_all(items)
        db.session.commit()

        # Create SoldItem entries for sold items
        for item in items:
            if item.sold:
                sold_entry = SoldItem(
                    item_id=item.item_id,
                    seller_id=item.seller_id,
                    buyer_id=buyer.id,
                    price=item.minimum_price + 5
                )
                db.session.add(sold_entry)

        db.session.commit()
