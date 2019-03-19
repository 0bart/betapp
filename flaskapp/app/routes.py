from flask import render_template
from app import app
from app.db import get_last_n_matches

@app.route('/')
@app.route('/index')
def index():
    matches = get_last_n_matches(10)
    return render_template('index.html', title='Home', matches=matches)
