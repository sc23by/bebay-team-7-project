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
def testHomeRerouteP1(loggedInClientP1):
    print(f"{Colours.YELLOW}Testing homepage - P1 reroute:{Colours.RESET}")
    response = loggedInClientP1.get('/')
    assert response.status_code == 302
    assert b'/loggedIn' in response.data

def testHomeRerouteP2(loggedInClientP2):
    print(f"{Colours.YELLOW}Testing homepage - P2 reroute:{Colours.RESET}")
    response = loggedInClientP2.get('/')
    assert response.status_code == 302
    assert b'/expertHome' in response.data

def testHomeRerouteP3(loggedInClientP3):
    print(f"{Colours.YELLOW}Testing homepage - P3 reroute:{Colours.RESET}")
    response = loggedInClientP3.get('/')
    assert response.status_code == 302
    assert b'/managerHome' in response.data
