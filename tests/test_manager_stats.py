from app import app, db, bcrypt
from app.models import User, Item, SoldItem
from flask_login import current_user
from datetime import datetime, timedelta
from flask import template_rendered
from contextlib import contextmanager
from colours import Colours


def populate_databse():
    with app.app_context():
        
        # Create users
        seller = User(
            username='seller',
            email='seller@example.com',
            password=bcrypt.generate_password_hash('password'),
            first_name='Seller',
            last_name='Lastname'
        )
        buyer = User(
            username='buyer',
            email='buyer@example.com',
            password=bcrypt.generate_password_hash('password'),
            first_name='Buyer',
            last_name='Lastname'
        )
        db.session.add_all([seller, buyer])
        db.session.commit()

        # Add test items
        items = [
            Item(
                seller_id=seller.id,
                item_name="apel1",
                description="Wow what an item",
                minimum_price=10,
                shipping_cost=5.50,
                days=3,
                hours=2,
                minutes=30,
                item_image="test_image.jpg",
                date_time=datetime(2025, 3, 21, 13, 30, 8, 586181),
                expiration_time=datetime(2025, 3, 21, 13, 10, 0, 0),
                approved=False,
                site_fee_percentage=1.0,
                expert_fee_percentage=4.0,
                sold=True,
                category="other"
            ),
            Item(
                seller_id=seller.id,
                item_name="apel2",
                description="Wow what an item",
                minimum_price=20,
                shipping_cost=5.50,
                days=3,
                hours=2,
                minutes=30,
                item_image="test_image.jpg",
                date_time=datetime(2025, 3, 21, 13, 30, 8, 586181),
                expiration_time=datetime(2025, 3, 21, 13, 10, 0, 0),
                approved=False,
                site_fee_percentage=2.0,
                expert_fee_percentage=2.0,
                sold=True,
                category="other"
            ),
            Item(
                seller_id=seller.id,
                item_name="apel3",
                description="Wow what an item",
                minimum_price=100,
                shipping_cost=5.50,
                days=3,
                hours=2,
                minutes=30,
                item_image="test_image.jpg",
                date_time=datetime(2025, 3, 21, 13, 30, 8, 586181),
                expiration_time=datetime(2025, 3, 21, 13, 10, 0, 0),
                approved=False,
                site_fee_percentage=1.0,
                expert_fee_percentage=3.0,
                sold=True,
                category="other"
            ),
            Item(
                seller_id=seller.id,
                item_name="apel4",
                description="Wow what an item",
                minimum_price=155,
                shipping_cost=5.50,
                days=3,
                hours=2,
                minutes=30,
                item_image="test_image.jpg",
                date_time=datetime(2025, 3, 21, 13, 30, 8, 586181), # doesnt matte, only checks sold at time
                expiration_time=datetime(2025, 3, 21, 13, 10, 0, 0),
                approved=False,
                site_fee_percentage=1.0,
                expert_fee_percentage=9.0,
                sold=True,
                category="other"
            ),
        ]

        db.session.add_all(items)
        db.session.commit()

        # Create SoldItem entries for sold items
        for item in items:
            if item.sold:
                sold_entry = SoldItem(
                    item_id=item.item_id,
                    seller_id=item.seller_id,
                    buyer_id=buyer.id,
                    price=item.minimum_price + 5,
                    sold_at = datetime.now() - timedelta(days=3) # 3 days before, all will be same date
                )
                db.session.add(sold_entry)

        db.session.commit()


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


def test_manager_weekly_cost(loggedInClientP3):
    print(f"{Colours.YELLOW}Testing manager stats - display correct values:{Colours.RESET}")

    populate_databse()

    with captured_templates() as templates:
        response = loggedInClientP3.get('/manager/statistics')

        assert current_user.priority == 3, f"Expected priority 3, but got {current_user.priority}"
        assert response.status_code == 200
        assert len(templates) > 0

    _, context = templates[0]
    # check if financial values are present handed to template
    assert 'total_revenue' in context
    assert 'total_profit' in context
    assert 'generated_percentage' in context

    assert isinstance(context['total_revenue'], (int, float))
    assert isinstance(context['total_profit'], (int, float))
    assert isinstance(context['generated_percentage'], (int, float))

    # check if weekly data is present
    assert 'week_labels' in context
    assert 'values' in context

    week_labels = context['week_labels']
    values = context['values']
    totalr = context['total_revenue']
    totalp = context['total_profit']

    assert isinstance(week_labels, list)
    assert isinstance(values, list)
    assert len(week_labels) == 4
    assert len(values) == 4

    # ensure values are numeric
    for value in values:
        assert isinstance(value, (int, float))

    # ensure image data is passed correctly
    assert 'img_data' in context
    assert isinstance(context['img_data'], str)

    assert totalr == 305.0
    assert totalp >= 3.3
    assert values == [0, 0, 3.3000000000000003, 0]
