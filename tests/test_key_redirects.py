# test web page redirects
from colours import Colours

'''
Testing routes with logged out client
'''
def test_guest_redirect(client):
    print(f"{Colours.YELLOW}Testing reroute - logged out, reroute to guest page:{Colours.RESET}")
    response = client.get('/')
    assert response.status_code == 200
    assert b'<!-- Guest Home Page, displayes listed items -->' in response.data # will need changing

'''
Testing routes with logged in client
'''
def test_user_rerouteP1(loggedInClientP1):
    print(f"{Colours.YELLOW}Testing reroute - P1 reroute:{Colours.RESET}")
    response = loggedInClientP1.get('/')
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/user")

def test_expert_rerouteP2(loggedInClientP2):
    print(f"{Colours.YELLOW}Testing reroute - P2 reroute:{Colours.RESET}")
    response = loggedInClientP2.get('/')
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/expert/assignments")

def test_manager_rerouteP3(loggedInClientP3):
    print(f"{Colours.YELLOW}Testing reroute - P3 reroute:{Colours.RESET}")
    response = loggedInClientP3.get('/')
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/manager")

def test_logout_route(loggedInClientP1):
    print(f"{Colours.YELLOW}Testing Logout route - P1 reroute:{Colours.RESET}")

    response = loggedInClientP1.get('/logout')
    assert response.status_code == 302
    # check for redirect to main page route
    assert response.headers["Location"].endswith("/")

    # check cant access protected pages anymore
    response_after_logout = loggedInClientP1.get('/user/account')

    assert response_after_logout.status_code == 302
    assert "/login" in response_after_logout.headers["Location"]