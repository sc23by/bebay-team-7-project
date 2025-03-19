#!/bin/bash

# clear prevous migrations, instances and cache if exist
rm -rf migrations/ instance/ __pycache__

# Create virtual environment
python3 -m venv flask

# Activate virtual environment
source flask/bin/activate

# Install dependencies
<<<<<<< HEAD
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
=======
flask/bin/pip install flask 
flask/bin/pip install flask-login 
flask/bin/pip install flask-mail 
flask/bin/pip install flask-sqlalchemy 
flask/bin/pip install flask-migrate 
flask/bin/pip install flask-whooshalchemy 
flask/bin/pip install flask-wtf 
flask/bin/pip install flask-bcrypt
flask/bin/pip install flask-babel 
flask/bin/pip install email_validator 
flask/bin/pip install coverage 
flask/bin/pip install pytest
flask/bin/pip install matplotlib
flask/bin/pip install flask-socketio
flask/bin/pip install stripe
>>>>>>> 6de516a024334d77eee9d410aa49e65c30c0be21


flask db init
flask db migrate -m "Initial migration"
flask db upgrade

export FLASK_APP=run.py
export FLASK_DEBUG=1

# Confirm completion
echo "Virtual environment setup complete. Use 'source flask/bin/activate' to activate."
