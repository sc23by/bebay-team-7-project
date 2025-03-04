#tests for the register route

from app import app, db, bcrypt
from app.models import User
from colours import Colours

'''
Testing routes with logged out client
'''
def test_register_validUser(client):
    print(f"{Colours.YELLOW}Testing register page- registering a user:{Colours.RESET}")
    response = client.post('/register', data={
        'first_name': 'test',
        'last_name': 'user',
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'Test@1234',
        'confirm_password': 'Test@1234'
    }, follow_redirects=True)

    # check if user was added to the database
    user = User.query.filter_by(username='testuser').first()
    assert user is not None
    assert user.email == 'test@example.com'
    
    # ensure redirect to login page after registering
    assert response.status_code == 200
    assert b'<h1>Login</h1>' in response.data

def test_register_duplicate_username(client):
    print(f"{Colours.YELLOW}Testing register page - duplicate username:{Colours.RESET}")

    # create user to compare to
    with app.app_context():
        user = User(username='testuser',
                    email='existing@example.com',
                    password=bcrypt.generate_password_hash('password'),
                    first_name='firstname',
                    last_name='lastname')
        db.session.add(user)
        db.session.commit() 

    # register user with same username but all other details are different
    response = client.post('/register', data={
        'first_name': 'test',
        'last_name': 'user',
        'username': 'testuser',
        'email': 'new@example.com',
        'password': 'NewPassword1!',
        'confirm_password': 'NewPassword1!'
    }, follow_redirects=True)

    assert b'Username already exists' in response.data
    assert response.status_code == 200


def test_register_duplicate_email(client):
    print(f"{Colours.YELLOW}Testing register page - duplicate email:{Colours.RESET}")

    # create user to compare to
    with app.app_context():
        user = User(username='testuser',
                    email='existing@example.com',
                    password=bcrypt.generate_password_hash('password'),
                    first_name='firstname',
                    last_name='lastname')
        db.session.add(user)
        db.session.commit() 

    # register user with same username but all other details are different
    response = client.post('/register', data={
        'first_name': 'test',
        'last_name': 'user',
        'username': 'Newuser',
        'email': 'existing@example.com',
        'password': 'NewPassword1!',
        'confirm_password': 'NewPassword1!'
    }, follow_redirects=True)

    assert b'Email already exists' in response.data
    assert response.status_code == 200


def test_register_email_valid(client):
    response = client.post('/register', data={
        'first_name': 'test',
        'last_name': 'user',
        'username': 'testuser',
        'email': 'invalid@example',
        'password': 'NewPassword1!',
        'confirm_password': 'NewPassword1!'
    }, follow_redirects=True)

    assert b'Invalid email address.' in response.data
    assert response.status_code == 200


def test_register_rassword_mismatch(client):
    print(f"{Colours.YELLOW}Testing register page - missmatched passwords:{Colours.RESET}")

    response = client.post('/register', data={
        'first_name': 'test',
        'last_name': 'user',
        'username': 'Auser',
        'email': 'email@example.com',
        'password': 'FirstPassword1!!',
        'confirm_password': 'SecondPassword1!'
    }, follow_redirects=True)

    assert "Passwords must match." in response.data.decode()
    assert response.status_code == 200

def test_register_password_not_strong(client):
    print(f"{Colours.YELLOW}Testing register page - password not strong enough:{Colours.RESET}")

    response = client.post('/register', data={
        'first_name': 'test',
        'last_name': 'user',
        'username': 'Auser',
        'email': 'email@example.com',
        'password': 'firstpassword',
        'confirm_password': 'firstpassword'
    }, follow_redirects=True)

    assert "Password needs at least one uppercase letter." in response.data.decode()
    assert response.status_code == 200

    response = client.post('/register', data={
        'first_name': 'test',
        'last_name': 'user',
        'username': 'Auser',
        'email': 'email@example.com',
        'password': 'FirstPassword',
        'confirm_password': 'FirstPassword'
    }, follow_redirects=True)

    assert "Password needs at least one number." in response.data.decode()
    assert response.status_code == 200

def test_register_names_correct(client):
    print(f"{Colours.YELLOW}Testing register page - names correct format:{Colours.RESET}")

    response = client.post('/register', data={
        'first_name': 'testsuperextralongfirstnameeeeee',
        'last_name': 'testsuperextralonglastnameeeeeee',
        'username': 'Auser',
        'email': 'email@example.com',
        'password': 'Firstpassword1',
        'confirm_password': 'Firstpassword1'
    }, follow_redirects=True)

    assert "First name must be 2-30 characters." in response.data.decode()
    assert "Last name must be 2-30 characters." in response.data.decode()
    assert response.status_code == 200

    response = client.post('/register', data={
        'first_name': 'test!',
        'last_name': 'user!',
        'username': 'Auser',
        'email': 'email@example.com',
        'password': 'Firstpassword1',
        'confirm_password': 'Firstpassword1'
    }, follow_redirects=True)

    assert "First name should only contain letters." in response.data.decode()
    assert "Last name should only contain letters." in response.data.decode()
    assert response.status_code == 200

'''
Testing routes with logged in client (p1)
'''

def test_register_authenticated(loggedInClientP1):
    print(f"{Colours.YELLOW}Testing register page - reroute to p1 homepage:{Colours.RESET}")

    response = loggedInClientP1.get('/register')
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/user")
    