# test accounts page on the managers system

from app import app, db, bcrypt
from app.models import User
from colours import Colours


def test_manager_account_loads(loggedInClientP3):
    print(f"{Colours.YELLOW}Testing manager accounts page - page loads correctly:{Colours.RESET}")

    response = loggedInClientP3.get('/manager/accounts')
    assert response.status_code == 200
    assert b'testuser3' in response.data

def test_manager_account_change_priority(loggedInClientP3):
    print(f"{Colours.YELLOW}Testing manager accounts page - change account priority:{Colours.RESET}")

    with app.app_context():
        user = User(username='promotion',
                    email='existing@example.com',
                    password=bcrypt.generate_password_hash('password'),
                    first_name='firstname',
                    last_name='lastname',
                    priority=1)
        db.session.add(user)
        db.session.commit()
        priority = user.priority
        username = user.username

    response = loggedInClientP3.get(f'/manager/accounts/{username}/2')
    assert response.status_code == 302

    with app.app_context():
        updated_user = User.query.filter_by(username=username).first()
        assert updated_user is not None
        assert updated_user.priority != priority
        assert updated_user.priority == 2 