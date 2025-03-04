# test list item route

from app import app, db
from app.models import Item
import io
# import for direct file upload in testing
from werkzeug.datastructures import FileStorage

from colours import Colours


'''
Testing route with logged out client
'''
def test_unauthenticated_user_redirect(client):
    print(f"{Colours.YELLOW}Testing list items page - reroute unauthenticated user to login:{Colours.RESET}")

    response = client.get('/user/list_item')
    assert response.status_code == 302
    assert response.headers["Location"].startswith("/login")


def test_expert_redirect(loggedInClientP2):
    print(f"{Colours.YELLOW}Testing list items page - reroute expert user to expert page:{Colours.RESET}")

    response = loggedInClientP2.get('/user/list_item')
    assert response.status_code == 302
    assert response.headers["Location"].startswith("/expert")

def test_manager_redirect(loggedInClientP3):
    print(f"{Colours.YELLOW}Testing list items page - reroute manager user to manager page:{Colours.RESET}")

    response = loggedInClientP3.get('/user/list_item')
    assert response.status_code == 302
    assert response.headers["Location"].startswith("/manager")


"""
Authenticated users
"""

def test_list_item_page_access(loggedInClientP1):
    print(f"{Colours.YELLOW}Testing list items page - correct page access:{Colours.RESET}")

    response = loggedInClientP1.get('/user/list_item')
    assert response.status_code == 200
    assert b'List an Item' in response.data

def test_list_item(loggedInClientP1):
    print(f"{Colours.YELLOW}Testing list items page - correctly listing item:{Colours.RESET}")

    with app.app_context():
        initial_count = db.session.query(Item).count()
        
    data = {
            "item_name": "Test Item",
            "description": "A great test item!",
            "minimum_price": 10.99,
            "shipping_cost": 5.50,
            "days": 3,
            "hours": 2,
            "minutes": 30
        }
    image = FileStorage(
            stream=io.BytesIO(b"Fake image data"),
            filename="test_image.jpg",
            content_type="image/jpeg"
        )
    data["item_image"] = image

    response = loggedInClientP1.post('/user/list_item', data=data, follow_redirects=True)

    assert response.status_code == 200
    assert b"Item listed successfully!" in response.data


