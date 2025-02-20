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
    Requires valid username email, and password.
    """
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
