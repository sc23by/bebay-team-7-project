#!/bin/bash

# clear prevous migrations, instances and cache if exist
rm -rf migrations/ instance/ __pycache__

# Create virtual environment
python3 -m venv flask

# Activate virtual environment
source flask/bin/activate

# Install dependencies
pip install flask 
pip install flask-login 
pip install flask-mail 
pip install flask-sqlalchemy 
pip install flask-migrate 
pip install flask-whooshalchemy 
pip install flask-wtf 
pip install flask-bcrypt
pip install flask-babel 
pip install email_validator 
pip install coverage 
pip install pytest
pip install matplotlib
pip install flask-socketio
pip install stripe

flask db init
flask db migrate -m "Initial migration"
flask db upgrade

export FLASK_APP=run.py
export FLASK_DEBUG=1

# Confirm completion
echo "Virtual environment setup complete. Use 'source flask/bin/activate' to activate."
