#tests for the register route

from app import app, db, bcrypt
from app.models import User
from colours import Colours

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


def testRegisterEmailValid(client):
    response = client.post('/register', data={
        'firstName': 'test',
        'lastName': 'user',
        'username': 'testuser',
        'email': 'invalid@example',
        'password': 'NewPassword1!',
        'confirmPassword': 'NewPassword1!'
    }, follow_redirects=True)

    assert b'Invalid email address.' in response.data
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

    response = client.post('/register', data={
        'firstName': 'test',
        'lastName': 'user',
        'username': 'Auser',
        'email': 'email@example.com',
        'password': 'FirstPassword',
        'confirmPassword': 'FirstPassword'
    }, follow_redirects=True)

    assert "Password needs at least one number." in response.data.decode()
    assert response.status_code == 200

# FIXME - test name and lastname

'''
Testing routes with logged in client (p1)
'''

def testRegisterAuthenticated(loggedInClientP1):
    print(f"{Colours.YELLOW}Testing register page - reroute to p1 homepage:{Colours.RESET}")

    response = loggedInClientP1.get('/register')
    assert response.status_code == 302
    assert b'/loggedIn' in response.data
    