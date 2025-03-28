from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, FloatField, TimeField, DateField, BooleanField, SelectField, DecimalField
from wtforms.validators import DataRequired, Length, EqualTo, Regexp, ValidationError, Email, NumberRange
from flask_wtf.file import FileField, FileAllowed

CATEGORY_CHOICES = [
    ('electronics', 'Electronics'),
    ('fashion', 'Fashion & Accessories'),
    ('books_media', 'Books, Movies, & Music'),
    ('home_garden', 'Home & Garden'),
    ('toys_games', 'Toys & Games'),
    ('sports_outdoors', 'Sports & Outdoors'),
    ('automotive', 'Automotive'),
    ('collectibles_art', 'Collectibles & Art'),
    ('other', 'Other')
]

class EditExpertiseForm(FlaskForm):
    expertise = SelectField(
        'Your Area of Expertise',
        choices=CATEGORY_CHOICES,
        validators=[DataRequired()]
    )
    update_expertise = SubmitField('Update Expertise')


# Custom password validator
def strong_password(form, field):
    """
    Enforce strong passwords with uppercase, lowercase, and numbers.
    """
    password = field.data
    if not any(char.isupper() for char in password):
        raise ValidationError('Password needs at least one uppercase letter.')
    if not any(char.islower() for char in password):
        raise ValidationError('Password needs at least one lowercase letter.')
    if not any(char.isdigit() for char in password):
        raise ValidationError('Password needs at least one number.')
    if len(password) < 8:
        raise ValidationError('Password must be at least 8 characters.')

# Login form for users
class LoginForm(FlaskForm):
    """
    Requires username and password.
    """
    username = StringField('Username', validators=[
        DataRequired(), 
        Length(min=3, max=20, message="Username must be 3-20 characters.")
    ])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# Registration form for users
class RegistrationForm(FlaskForm):
    """
    Requires valid username, email, first name, last name, and password.
    """
    first_name = StringField('First Name', validators=[
        DataRequired(), 
        Length(min=2, max=30, message="First name must be 2-30 characters."),
        Regexp('^[A-Za-z]+$', message="First name should only contain letters.")
    ])
    
    last_name = StringField('Last Name', validators=[
        DataRequired(), 
        Length(min=2, max=30, message="Last name must be 2-30 characters."),
        Regexp('^[A-Za-z]+$', message="Last name should only contain letters.")
    ])
    username = StringField('Username', validators=[
        DataRequired(), 
        Length(min=3, max=20, message="Username must be 3-20 characters."),
        Regexp('^[A-Za-z0-9_]+$', message="Only letters, numbers, and underscores allowed.")
    ])
    email = StringField('Email', validators=[
        DataRequired(), 
        Email(message="Invalid email address.")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        strong_password
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message="Passwords must match.")
    ])
    submit = SubmitField('Register')

# Form for side bar
class SideBarForm(FlaskForm):
    """
    Buttons for navigation through profile section 
    """
    info = SubmitField('Info')
    my_bids = SubmitField('Bids')
    my_listings = SubmitField('Listings')
    watchlist = SubmitField('Watchlist')
    notifications = SubmitField('Notifications')
    past_orders = SubmitField('Past Orders')
    logout = SubmitField('Logout')

# Form for changing user information
class UserInfoForm(FlaskForm):
    """
    Allows user to update user information
    """
    first_name = StringField('First Name', validators=[
        Length(min=2, max=30),
        Regexp('^[A-Za-z]+$')
    ])

    last_name = StringField('Last Name', validators=[
        Length(min=2, max=30),
        Regexp('^[A-Za-z]+$')
    ]) 

    update_info = SubmitField('Edit Name')

# Form for changing password
class ChangeUsernameForm(FlaskForm):
    """
    Allows user to change username
    """
    username = StringField('Username', validators=[
        Length(min=3, max=20),
        Regexp('^[A-Za-z0-9_]+$')
    ])

    update_username = SubmitField('Edit Username')

# Form for changing password
class ChangeEmailForm(FlaskForm):
    """
    Allows user to change email
    """
    email = StringField('Email', validators=[
        Email()
    ])

    update_email = SubmitField('Edit Email')

# Form for changing password
class ChangePasswordForm(FlaskForm):
    """
    Allows user to change password
    """
    new_password = PasswordField('Password', validators=[
        strong_password
    ])

    confirm_password = PasswordField('Confirm Password', validators=[
        EqualTo('new_password')
    ])

    update_privacy = SubmitField('Change Password')

# Form for changing card and shipping information
class CardInfoForm(FlaskForm):
    """
    Allows user to update card information
    """
    card_number = StringField('Card Number', validators=[
    ])

    shipping_address = StringField('Shipping Address', validators=[
    ])

    update_card = SubmitField('Update Card Info')


class ListItemForm(FlaskForm):
    item_name = StringField(
        'Item Name', 
        validators=[DataRequired(), Length(max=100)]
    )
    
    description = StringField(
        'Description', 
        validators=[DataRequired(), Length(max=500)]
    )
    
    category = SelectField(
        'Category',
        choices=CATEGORY_CHOICES,
        validators=[DataRequired()]
    )
    
    minimum_price = DecimalField(
        'Starting Price (£)',
        places=2, 
        validators=[DataRequired(), NumberRange(min=0)],
        render_kw={"step": "0.01", "min": "0.01", "class": "currency-input"}
    )
    
    item_image = FileField(
        'Upload Image', 
        validators=[DataRequired()]
    )
    
    # Dropdowns for duration selection
    days = SelectField(
        'Days', 
        choices=[(str(i), f"{i} day{'s' if i != 1 else ''}") for i in range(5)], 
        validators=[DataRequired()]
    )
    
    hours = SelectField(
        'Hours', 
        choices=[(str(i), f"{i} hour{'s' if i != 1 else ''}") for i in range(24)], 
        validators=[DataRequired()]
    )

    minutes = SelectField(
        'Minutes', 
        choices=[(str(i), f"{i} minute{'s' if i != 1 else ''}") for i in range(0, 60, 1)], 
        validators=[DataRequired()]
    )
    
    shipping_cost = DecimalField(
        'Shipping Cost (£)', 
        places=2, 
        validators=[DataRequired(), NumberRange(min=0)],
        render_kw={"step": "0.01", "min": "0.01", "class": "currency-input"}
    )

    authenticate = BooleanField('Would you like to authenticate this item?')
    
    submit = SubmitField('List Item')


class BidForm(FlaskForm):
    bid_amount = DecimalField("Your Bid (£)",
        places=2,
        validators=[DataRequired(),
        NumberRange(min=0.01)],
        render_kw={"step": "0.01", "min": "0.0.1", "class": "currency-input"})

    submit = SubmitField("Place Bid")

class EditExpertiseForm(FlaskForm):
    expertise = SelectField(
        'Area of Expertise',
        choices=CATEGORY_CHOICES,
        validators=[DataRequired()]
    )
    update_expertise = SubmitField('Update Expertise')