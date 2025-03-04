# account route tests

from colours import Colours

"""
Non Authenticated users, redirects
"""

def test_unauthenticated_user_redirect(client):
    print(f"{Colours.YELLOW}Testing user pages - reroute unauthenticated user to login:{Colours.RESET}")

    response = client.get('/user/account')
    assert response.status_code == 302
    assert response.headers["Location"].startswith("/login")

    response = client.get('/user/my_listings')
    assert response.status_code == 302
    assert response.headers["Location"].startswith("/login")

    response = client.get('/user/watchlist')
    assert response.status_code == 302
    assert response.headers["Location"].startswith("/login")


"""
Authenticated users, account redirects
"""

def test_user_account_redirect(loggedInClientP1):
    print(f"{Colours.YELLOW}Testing user account page - reroutes:{Colours.RESET}")

    response = loggedInClientP1.post('/user/account', data={"sidebar": True, "my_listings": True}, follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/user/my_listings")

    response = loggedInClientP1.post('/user/account', data={"sidebar": True, "watchlist": True}, follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/user/watchlist")

    response = loggedInClientP1.post('/user/account', data={"sidebar": True, "notifications": True}, follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/user/notifications")

    response = loggedInClientP1.post('/user/account', data={"sidebar": True, "logout": True}, follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/logout")

def test_user_my_listings_redirect(loggedInClientP1):
    print(f"{Colours.YELLOW}Testing user my_listings page - reroutes:{Colours.RESET}")

    response = loggedInClientP1.post('/user/my_listings', data={"sidebar": True, "my_listings": True}, follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/user/my_listings")

    response = loggedInClientP1.post('/user/my_listings', data={"sidebar": True, "watchlist": True}, follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/user/watchlist")

    response = loggedInClientP1.post('/user/my_listings', data={"sidebar": True, "notifications": True}, follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/user/notifications")

    response = loggedInClientP1.post('/user/my_listings', data={"sidebar": True, "logout": True}, follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/logout")
    

def test_user_watchlist_redirect(loggedInClientP1):
    print(f"{Colours.YELLOW}Testing user watchlist page - reroutes:{Colours.RESET}")

    response = loggedInClientP1.post('/user/watchlist', data={"sidebar": True, "my_listings": True}, follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/user/my_listings")

    response = loggedInClientP1.post('/user/watchlist', data={"sidebar": True, "watchlist": True}, follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/user/watchlist")

    response = loggedInClientP1.post('/user/watchlist', data={"sidebar": True, "notifications": True}, follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/user/notifications")

    response = loggedInClientP1.post('/user/watchlist', data={"sidebar": True, "logout": True}, follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/logout")

def test_user_notifications_redirect(loggedInClientP1):
    print(f"{Colours.YELLOW}Testing user notifications page - reroutes:{Colours.RESET}")

    response = loggedInClientP1.post('/user/notifications', data={"sidebar": True, "my_listings": True}, follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/user/my_listings")

    response = loggedInClientP1.post('/user/notifications', data={"sidebar": True, "watchlist": True}, follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/user/watchlist")

    response = loggedInClientP1.post('/user/notifications', data={"sidebar": True, "notifications": True}, follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/user/notifications")

    response = loggedInClientP1.post('/user/notifications', data={"sidebar": True, "logout": True}, follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/logout")


# FIXME - test route works for logged in pages (display correct username and information)
