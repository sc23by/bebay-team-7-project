# test web page redirects
from colours import Colours

'''
Testing routes with logged out client
'''
def testHome(client):
    print(f"{Colours.YELLOW}Testing reroute - logged out, reroute to guest page:{Colours.RESET}")
    response = client.get('/')
    assert response.status_code == 200
    assert b'guest_home' in response.data

'''
Testing routes with logged in client
'''
def testUserRerouteP1(loggedInClientP1):
    print(f"{Colours.YELLOW}Testing reroute - P1 reroute:{Colours.RESET}")
    response = loggedInClientP1.get('/')
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/user")

def testExpertRerouteP2(loggedInClientP2):
    print(f"{Colours.YELLOW}Testing reroute - P2 reroute:{Colours.RESET}")
    response = loggedInClientP2.get('/')
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/expert/assignments")

def testManagerRerouteP3(loggedInClientP3):
    print(f"{Colours.YELLOW}Testing reroute - P3 reroute:{Colours.RESET}")
    response = loggedInClientP3.get('/')
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/manager")

def testLogoutRoute(loggedInClientP1):
    print(f"{Colours.YELLOW}Testing Logout route - P1 reroute:{Colours.RESET}")
    response = loggedInClientP1.get('/logout')
    assert response.status_code == 302
    # check for redirect to main page route
    assert response.headers["Location"].endswith("/")