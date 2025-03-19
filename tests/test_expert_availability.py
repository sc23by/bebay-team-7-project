from app import app, db, bcrypt
from app.models import ExpertAvailabilities, User
from flask_login import current_user
from datetime import date, time, datetime, timedelta
from flask import template_rendered
from contextlib import contextmanager

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
    print(f"{Colours.YELLOW}Testing expert set availability - clear all availability:{Colours.RESET}")

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


@contextmanager
def captured_templates():
    '''
    allow acess to variables being passed into the template
    '''
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((template, context))

    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)


def test_manager_view_currently_avialable(loggedInClientP3):
    print(f"{Colours.YELLOW}Testing managers view availability - manaagers view currently available experts :{Colours.RESET}")

    with app.app_context():
        for i in range(3):
            expert = User(
                username=f'expert{i}',
                email=f'expert{i}@example.com',
                password=bcrypt.generate_password_hash('password'),
                first_name='Test', 
                last_name='User', 
                priority=2)
            db.session.add(expert)
        db.session.commit()


        current_datetime = datetime.utcnow()

        # Get the current date (today)
        current_date = current_datetime.date()
        splitDates = [current_date.strftime('%Y-%m-%d'), (current_date + timedelta(days=5)).strftime('%Y-%m-%d')]
        splitStartTimes = [(current_datetime + timedelta(hours=4)).strftime('%H:%M'), (current_datetime + timedelta(hours=4)).strftime('%H:%M')]


        for date, start_time in zip(splitDates, splitStartTimes):
            date_obj = datetime.strptime(date, '%Y-%m-%d').date()
            start_time_obj = datetime.strptime(start_time, '%H:%M').time()

            availability = ExpertAvailabilities(
                user_id=2,
                date=date_obj,
                start_time=start_time_obj,
                duration=1
            )
            db.session.add(availability)
        db.session.commit()

    with captured_templates() as templates:
        response = loggedInClientP3.get('/manager/expert_availability')
    
    assert response.status_code == 200
    assert len(templates) > 0
    # get context (and template)
    _ , context = templates[0]
    # get set of experts that r avalable (should be only 1 and with id 2)
    available_experts_48h = context['available_experts_48h']
    assert 2 in available_experts_48h
    assert len(available_experts_48h) == 1
