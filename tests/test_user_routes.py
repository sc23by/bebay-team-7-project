# account route tests

from colours import Colours

def test_user_reroute(client):
    print(f"{Colours.YELLOW}Testing user page - reroute unauthenticated account:{Colours.RESET}")

    response = client.get('/user/account')
    assert response.status_code == 302
    assert response.headers["Location"].startswith("/login")

    response = client.get('/user/my_listings')
    assert response.status_code == 302
    assert response.headers["Location"].startswith("/login")

    response = client.get('/user/watchlist')
    assert response.status_code == 302
    assert response.headers["Location"].startswith("/login")

# FIXME - test button redirects (4)

def test_user_mylistings_redirect(loggedInClientP1):
    """
    Test that submitting 'my_listings' in the sidebar form redirects to /user/my_listings.
    """
    response = loggedInClientP1.post('/user/account', data={"sidebar": True, "my_listings": True}, follow_redirects=False)

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/user/my_listings")

# FIXME - test route works for logged in pages (display correct username and information)


# FIXME - test listings returns correct html
# FIXME - test watchlist returns correct html
# FIXME - test notifications returns correct html

