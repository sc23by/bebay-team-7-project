# checks account infro page (ensure data can be updated)


from app import app, db, bcrypt
from app.models import User, PaymentInfo
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


# FIXME - add name update ytests

def test_change_valid_username(loggedInClientP1):
    print(f"{Colours.YELLOW}Testing account info page - update username:{Colours.RESET}")

    response = loggedInClientP1.post("/user/account", data={
        "username": "newusername",
        "update_username": 'Edit'
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
        'update_username': 'Edit'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Username already exists. Please choose a different one.' in response.data

    with app.app_context():
        assert current_user.username != 'other_user'

def test_change_unvalid_username(loggedInClientP1):
    print(f"{Colours.YELLOW}Testing account info page - username invalid:{Colours.RESET}")

    response = loggedInClientP1.post("/user/account", data={
        'username': 'testuser()',
        'update_username': 'Edit'
    }, follow_redirects=True)

    assert response.status_code == 200#
    # FIXME - add validation for flash message

    with app.app_context():
        assert current_user.username != 'testuser()'


def test_change_valid_email(loggedInClientP1):
    print(f"{Colours.YELLOW}Testing account info page - update email:{Colours.RESET}")

    response = loggedInClientP1.post("/user/account", data={
        'email': 'newemail@email.com',
        "update_email": 'Edit'
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
        "update_email": 'Edit'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Email already exists. Please choose a different one.' in response.data

    with app.app_context():
        assert current_user.email != "existing@example.com"


def test_change_unvalid_email(loggedInClientP1):
    print(f"{Colours.YELLOW}Testing account info page - email invalid:{Colours.RESET}")

    response = loggedInClientP1.post("/user/account", data={
        'email': 'invalid@',
        "update_email": 'Edit'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Invalid email address.' in response.data

    with app.app_context():
        assert current_user.username != 'invalid@'


def test_change_passowrd(loggedInClientP1):
    print(f"{Colours.YELLOW}Testing account info page - update password:{Colours.RESET}")

    response = loggedInClientP1.post('/user/account', data={
        'new_password': 'newValidPassword123',
        'confirm_password': 'newValidPassword123',
        'update_privacy': 'Change Password'
    },follow_redirects=True)

    assert response.status_code == 200
    assert b'Password updated successfully!' in response.data

    with app.app_context():
        assert bcrypt.check_password_hash(current_user.password, 'newValidPassword123')

def test_missmatching_passowrds(loggedInClientP1):
    print(f"{Colours.YELLOW}Testing account info page -passwords missmatch:{Colours.RESET}")

    response = loggedInClientP1.post('/user/account', data={
        'new_password': 'newValidPassword123',
        'confirm_password': 'differentValidPassword123',
        'update_privacy': 'Change Password'
    },follow_redirects=True)

    assert response.status_code == 200
    assert b'Passwords do not match.' in response.data

    with app.app_context():
        assert not bcrypt.check_password_hash(current_user.password, 'newValidPassword123')
        assert not bcrypt.check_password_hash(current_user.password, 'differentValidPassword123')


def test_update_shipping_card(loggedInClientP1):
    print(f"{Colours.YELLOW}Testing account info page - card and shipping update:{Colours.RESET}")

    with app.app_context():
        payment_info = PaymentInfo(user_id=current_user.id)
        db.session.add(payment_info)
        db.session.commit()

    response = loggedInClientP1.post('/user/account', data={
        'card_number': '12345678',
        'shipping_address': 'my address',
        'update_card': 'Update Card Info'
    },follow_redirects=True)

    assert response.status_code == 200

    with app.app_context():
        payment_info = PaymentInfo.query.filter_by(user_id=current_user.id).first()
        assert payment_info.shipping_address == 'my address'
