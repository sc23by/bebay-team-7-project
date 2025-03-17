from app import app, db
from app.models import ExpertAvailabilities
from flask_login import current_user
from datetime import date, time

from colours import Colours

def test_load_page(loggedInClientP2):
    print(f"{Colours.YELLOW}Testing expert set availabilty - load page:{Colours.RESET}")

    response = loggedInClientP2.get('/expert/availability')

    assert response.status_code == 200
    assert b'<table id="availability-table">' in response.data
    assert ExpertAvailabilities.query.filter_by(user_id= current_user.id).count() == 0

def test_set_availability(loggedInClientP2):
    print(f"{Colours.YELLOW}Testing expert set availabilty - set an experts availability:{Colours.RESET}") 

    assert ExpertAvailabilities.query.filter_by(user_id= current_user.id).count() == 0

    response = loggedInClientP2.post('/expert/availability', data={
        'date': '2025-03-18,2025-03-19',
        'start_time': '10:00,14:00'
    }, follow_redirects=True)


    # page tests
    assert response.status_code == 200
    assert b"Expert Availability" in response.data
    response = loggedInClientP2.get('/expert/availability')
    assert response.status_code == 200

    # db tests
    availabilities = ExpertAvailabilities.query.filter_by(user_id=current_user.id).all()
    assert len(availabilities) == 2  
    assert any(a.start_time.strftime("%H:%M") == "10:00" for a in availabilities)
    assert any(a.start_time.strftime("%H:%M") == "14:00" for a in availabilities)


def test_clear_availability(loggedInClientP2):
    print(f"Testing expert set availability - clear all availability:")

    with app.app_context():
        availability = ExpertAvailabilities(
            user_id=current_user.id,
            date=date(2025, 3, 18),
            start_time=time(10, 0),
            duration=1
        )
        db.session.add(availability)
        db.session.commit()

    availabilities = ExpertAvailabilities.query.filter_by(user_id=current_user.id).all()
    assert len(availabilities) == 1

    response = loggedInClientP2.post('/expert/availability', data={
        'date': '',
        'start_time': ''
    }, follow_redirects=True)

    assert response.status_code == 200
    with app.app_context():
        availabilities_after_clear = ExpertAvailabilities.query.filter_by(user_id=current_user.id).all()
        assert len(availabilities_after_clear) == 0
