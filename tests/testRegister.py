#tests for the register route
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db, bcrypt
from app.models import User
from flask import url_for
import pytest
from colours import Colours


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
                         firstName='Test', 
                         lastName='User', 
                         priority=1)
        db.session.add(test_user)
        db.session.commit()

    # Log in the user
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'password'
    }, follow_redirects=True)

    assert response.status_code == 200  # Ensure login was successful
    return client


'''
Testing routes with logged out client
'''
def testRegisterValidUser(client):
    print(f"{Colours.YELLOW}Testing register page- registering a user:{Colours.RESET}")
    response = client.post('/register', data={
        'firstName': 'test',
        'lastName': 'user',
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'Test@1234',
        'confirmPassword': 'Test@1234'
    }, follow_redirects=True)

    # check if user was added to the database
    user = User.query.filter_by(username='testuser').first()
    assert user is not None
    assert user.email == 'test@example.com'
    
    # ensure redirect to login page after registering
    assert response.status_code == 200
    assert b'<h1>Login</h1>' in response.data

def testRegisterDuplicateUsername(client):
    print(f"{Colours.YELLOW}Testing register page - duplicate username:{Colours.RESET}")

    # create user to compare to
    with app.app_context():
        user = User(username='testuser',
                    email='existing@example.com',
                    password=bcrypt.generate_password_hash('password'),
                    firstName='firstName',
                    lastName='lastnNme')
        db.session.add(user)
        db.session.commit() 

    # register user with same username but all other details are different
    response = client.post('/register', data={
        'firstName': 'test',
        'lastName': 'user',
        'username': 'testuser',
        'email': 'new@example.com',
        'password': 'NewPassword1!',
        'confirmPassword': 'NewPassword1!'
    }, follow_redirects=True)

    assert b'Username already exists' in response.data
    assert response.status_code == 200


def testRegisterDuplicateEmail(client):
    print(f"{Colours.YELLOW}Testing register page - duplicate email:{Colours.RESET}")

    # create user to compare to
    with app.app_context():
        user = User(username='testuser',
                    email='existing@example.com',
                    password=bcrypt.generate_password_hash('password'),
                    firstName='firstName',
                    lastName='lastnNme')
        db.session.add(user)
        db.session.commit() 

    # register user with same username but all other details are different
    response = client.post('/register', data={
        'firstName': 'test',
        'lastName': 'user',
        'username': 'Newuser',
        'email': 'existing@example.com',
        'password': 'NewPassword1!',
        'confirmPassword': 'NewPassword1!'
    }, follow_redirects=True)

    assert b'Email already exists' in response.data
    assert response.status_code == 200


def testRegisterPasswordMismatch(client):
    print(f"{Colours.YELLOW}Testing register page - missmatched passwords:{Colours.RESET}")

    response = client.post('/register', data={
        'firstName': 'test',
        'lastName': 'user',
        'username': 'Auser',
        'email': 'email@example.com',
        'password': 'FirstPassword1!!',
        'confirmPassword': 'SecondPassword1!'
    }, follow_redirects=True)

    assert "Passwords must match." in response.data.decode()
    assert response.status_code == 200

def testRegisterPasswordNotStrong(client):
    print(f"{Colours.YELLOW}Testing register page - password not strong enough:{Colours.RESET}")

    response = client.post('/register', data={
        'firstName': 'test',
        'lastName': 'user',
        'username': 'Auser',
        'email': 'email@example.com',
        'password': 'firstpassword',
        'confirmPassword': 'firstpassword'
    }, follow_redirects=True)

    assert "Password needs at least one uppercase letter." in response.data.decode()
    assert response.status_code == 200

#FIXME test email is valid
#FIXME test firstname lastname and username is correct form (length ect)

'''
Testing routes with logged out client
'''

def testRegisterAuthenticated(loggedInClientP1):
    print(f"{Colours.YELLOW}Testing register page - logged in:{Colours.RESET}")

    response = loggedInClientP1.get('/register')
    assert response.status_code == 302
    assert b'/loggedIn' in response.data
    