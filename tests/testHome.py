#tests for the register route

from colours import Colours

'''
Testing routes with logged out client
'''
def testHome(client):
    print(f"{Colours.YELLOW}Testing homepage - logged out:{Colours.RESET}")
    response = client.get('/')
    assert response.status_code == 200
    assert b'Main Page' in response.data

'''
Testing routes with logged in client
'''
def testHomeAuthenticated(loggedInClientP1):
    print(f"{Colours.YELLOW}Testing homepage - logged in:{Colours.RESET}")
    response = loggedInClientP1.get('/')
    assert response.status_code == 302
    assert b'/loggedIn' in response.data