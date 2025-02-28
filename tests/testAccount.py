# account route tests

from colours import Colours

def testRegisterValidUser(client):
    print(f"{Colours.YELLOW}Testing account page- reroute unauthenticated account:{Colours.RESET}")

    response = client.get('/account')
    assert response.status_code == 302
    assert b'/login' in response.data