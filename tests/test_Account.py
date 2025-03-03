# account route tests

from colours import Colours

def testRegisterValidUser(client):
    print(f"{Colours.YELLOW}Testing account page- reroute unauthenticated account:{Colours.RESET}")

    response = client.get('/user/account')
    assert response.status_code == 302
    assert b'/login' in response.data

# FIXME - test route works for logged in pages (display correct username and information)
# FIXME - test button redirects (4)

# FIXME - test listings returns correct html
# FIXME - test watchlist returns correct html
# FIXME - test notifications returns correct html

