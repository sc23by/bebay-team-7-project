#tests for the register route

from colours import Colours

'''
Testing routes with logged out client
'''
def testHome(client):
    print(f"{Colours.YELLOW}Testing homepage - logged out:{Colours.RESET}")
    response = client.get('/')
    assert response.status_code == 200
    assert b'Main Page' in response.data # Potential change needed

'''
Testing routes with logged in client
'''
def testHomeRerouteP1(loggedInClientP1):
    print(f"{Colours.YELLOW}Testing homepage - P1 reroute:{Colours.RESET}")
    response = loggedInClientP1.get('/')
    assert response.status_code == 302
    assert b'/user_home</a>' in response.data

def testHomeRerouteP2(loggedInClientP2):
    print(f"{Colours.YELLOW}Testing homepage - P2 reroute:{Colours.RESET}")
    response = loggedInClientP2.get('/')
    assert response.status_code == 302
    assert b'/expert_home</a>' in response.data

def testHomeRerouteP3(loggedInClientP3):
    print(f"{Colours.YELLOW}Testing homepage - P3 reroute:{Colours.RESET}")
    response = loggedInClientP3.get('/')
    assert response.status_code == 302
    assert b'/manager_home</a>' in response.data

def testLogoutRoute(loggedInClientP1):
    print(f"{Colours.YELLOW}Testing Logout route - P1 reroute:{Colours.RESET}")
    response = loggedInClientP1.get('/logout')
    assert response.status_code == 302
    # check for redirect to main page route
    assert b'<a href="/">/</a>' in response.data