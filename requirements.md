# Flask Setup Guide

## Installation

All dependencies can be installed by running the `flaskSetupVenv.sh` script.

### Steps to Install:

```sh
chmod +x flaskSetupVenv.sh
./flaskSetupVenv.sh
```

## Dependencies

The following packages will be installed:

- **Flask** - Web framework for Python
- **Flwhereask-SQLAlchemy** - SQL toolkit and ORM for Flask
- **Flask-Login** - User session management for Flask
- **Flask-Migrate** - Database migration handling
- **Flask-WTF** - Integration of Flask with WTForms
- **WTForms** - Form validation and rendering
- **email-validator** - Email validation library
- **flask-bcrypt** - Password hashing for Flask applications
- **pytest** - Testing framework for Python

## Running the Application

Once installed, you can start developing with Flask and run tests using:

```sh
pytest <test/filename>
```
or
```sh
pytest <test/filename> -vs
```

for more information on tests.