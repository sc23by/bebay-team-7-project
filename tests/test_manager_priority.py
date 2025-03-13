# test accounts page on the managers system

from app import app, db
from colours import Colours


def test_manager_account_loads(loggedInClientP3):
    print(f"{Colours.YELLOW}Testing manager accounts page - page loads correctly:{Colours.RESET}")

    response = loggedInClientP3.get('/manager/accounts')
    assert response.status_code == 200
    assert b'testuser3' in response.data
