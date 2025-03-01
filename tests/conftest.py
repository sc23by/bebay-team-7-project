# route test setup - discovered by all route tests
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db, bcrypt
from app.models import User
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
        test_user = User(username='testuser',
                         email='test@example.com',
                         password=bcrypt.generate_password_hash('password'),
                         first_name='Test', 
                         last_name='User', 
                         priority=1)
        db.session.add(test_user)
        db.session.commit()

    # log in the user
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'password'
    }, follow_redirects=True)

    assert response.status_code == 200
    return client

@pytest.fixture
def loggedInClientP2(client):
    with app.app_context():
        test_user = User(username='testuser',
                         email='test@example.com',
                         password=bcrypt.generate_password_hash('password'),
                         first_name='Test', 
                         last_name='User', 
                         priority=2)
        db.session.add(test_user)
        db.session.commit()

    # log in the user
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'password'
    }, follow_redirects=True)

    assert response.status_code == 200
    return client

@pytest.fixture
def loggedInClientP3(client):
    with app.app_context():
        test_user = User(username='testuser',
                         email='test@example.com',
                         password=bcrypt.generate_password_hash('password'),
                         first_name='Test', 
                         last_name='User', 
                         priority=3)
        db.session.add(test_user)
        db.session.commit()

    # log in the user
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'password'
    }, follow_redirects=True)

    assert response.status_code == 200
    return client