import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db, bcrypt
from app.models import User
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
def loggedInClient(client):
    client.get('/login')
    return client


'''
Testing routes with logged out client
'''
def testHome(client):
    print(f"{Colours.YELLOW}Testing homepage - logged out:{Colours.RESET}")
    response = client.get('/')
    assert response.status_code == 200

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


#FIXME test email is valid
#FIXME test pasword is strong enough

'''
Testing routes with logged out client
'''
def testHomeAuthenticated(loggedInClient):
    print(f"{Colours.YELLOW}Testing homepage - logged in:{Colours.RESET}")
    response = loggedInClient.get('/')
    assert response.status_code == 200

def testRegisterAuthenticated(loggedInClient):
    print(f"{Colours.YELLOW}Testing register page - logged in:{Colours.RESET}")
    response = loggedInClient.get('/register')
    assert response.status_code == 200
    assert b'<p> Now logged in </p>' in response.data  
