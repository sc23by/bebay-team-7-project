# checks account infro page (ensure data can be updated)


from app import app, db, bcrypt
from app.models import User
from flask_login import current_user

from colours import Colours

def test_account_page_loads(loggedInClientP1):
    print(f"{Colours.YELLOW}Testing account info page - page loads correctly:{Colours.RESET}")

    response = loggedInClientP1.get("/user/account")
    assert response.status_code == 200
    assert b'Account' in response.data
    assert b'First Name' in response.data
    assert b'Last Name' in response.data
    assert b'Username' in response.data
    assert b'Email' in response.data

def test_change_valid_username(loggedInClientP1):
    print(f"{Colours.YELLOW}Testing account info page - update username:{Colours.RESET}")

    response = loggedInClientP1.post("/user/account", data={
        "username": "newusername",
        "update_username": True
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Username updated successfully!' in response.data

    with app.app_context():
        assert current_user.username == "newusername"

def test_change_existing_username(loggedInClientP1):
    print(f"{Colours.YELLOW}Testing account info page - dont update if username already exists:{Colours.RESET}")

    with app.app_context():
        user = User(username='other_user',
                    email='existing@example.com',
                    password=bcrypt.generate_password_hash('password'),
                    first_name='firstname',
                    last_name='lastname')
        db.session.add(user)
        db.session.commit() 

    response = loggedInClientP1.post("/user/account", data={
        'username': 'other_user',
        'update_username': True
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Username already exists. Please choose a different one.' in response.data

    with app.app_context():
        assert current_user.username != 'other_user'

def test_change_unvalid_username(loggedInClientP1):
    print(f"{Colours.YELLOW}Testing account info page - username invalid:{Colours.RESET}")

    response = loggedInClientP1.post("/user/account", data={
        'username': 'testuser()',
        'update_username': True
    }, follow_redirects=True)

    assert response.status_code == 200

    with app.app_context():
        assert current_user.username != 'testuser()'


def test_change_valid_email(loggedInClientP1):
    print(f"{Colours.YELLOW}Testing account info page - update email:{Colours.RESET}")

    response = loggedInClientP1.post("/user/account", data={
        'email': 'newemail@email.com',
        "update_email": True
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Email updated successfully!' in response.data

    with app.app_context():
        assert current_user.email == "newemail@email.com"

def test_change_existing_email(loggedInClientP1):
    print(f"{Colours.YELLOW}Testing account info page - email already exists:{Colours.RESET}")

    with app.app_context():
        user = User(username='other_user',
                    email='existing@example.com',
                    password=bcrypt.generate_password_hash('password'),
                    first_name='firstname',
                    last_name='lastname')
        db.session.add(user)
        db.session.commit() 

    response = loggedInClientP1.post("/user/account", data={
        'email': 'existing@example.com',
        "update_email": True
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Email already exists. Please choose a different one.' in response.data

    with app.app_context():
        assert current_user.email != "existing@example.com"


def test_change_unvalid_email(loggedInClientP1):
    print(f"{Colours.YELLOW}Testing account info page - email invalid:{Colours.RESET}")

    response = loggedInClientP1.post("/user/account", data={
        'email': 'invalid@',
        "update_email": True
    }, follow_redirects=True)

    assert response.status_code == 200

    with app.app_context():
        assert current_user.username != 'invalid@'


