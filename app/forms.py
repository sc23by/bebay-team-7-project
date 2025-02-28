from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, Regexp, ValidationError, Email

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
    firstName = StringField('First Name', validators=[
        DataRequired(), 
        Length(min=2, max=30, message="First name must be 2-30 characters."),
        Regexp('^[A-Za-z]+$', message="First name should only contain letters.")
    ])
    
    lastName = StringField('Last Name', validators=[
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
    confirmPassword = PasswordField('Confirm Password', validators=[
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
    my_listings = SubmitField('My Listings')
    watchlist = SubmitField('My Watchlist')
    notifications = SubmitField('Notifications')

