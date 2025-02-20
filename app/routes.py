from app import app, db
from flask import render_template

@app.route('/')
def mainPage():
    return render_template('mainPage.html')

@app.route('/account')
def account():
    return render_template('account.html')
