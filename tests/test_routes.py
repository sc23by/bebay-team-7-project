import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
import pytest

'''
Creating fixtures to test routes with
client: unlogged in client
loggedInClient: client who has logged in
'''
@pytest.fixture
def client():
    print("\nSetting up the test client")
    with app.test_client() as client:
        yield client
    print("\nTearing down the test client")

@pytest.fixture
def loggedInClient(client):
    client.get('/login')
    return client

def test_home(client):
    print("Testing homepage - logged out:")
    response = client.get('/')
    assert response.status_code == 200

def test_home_authenticated(loggedInClient):
    print("Testing homepage - logged in:")
    response = loggedInClient.get('/')
    assert response.status_code == 200
