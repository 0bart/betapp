from flask import render_template
from app import app
from app.db import get_result_n_matches, get_fixture_n_matches

app.jinja_env.filters['zip'] = zip

@app.route('/')
@app.route('/about')
def index():
    return render_template('index.html', title='betapp - About')

@app.route('/tables')
@app.route('/tables/<int:page>')
def tables(page=0):
    total_fix, fixtures = get_fixture_n_matches(5, page)
    results = get_result_n_matches(15)
    return render_template('tables.html', title='betapp - Tables', fixtures=fixtures, total_fix=total_fix, page=page,
                           results=results)

@app.route('/sim')
def sim():
    return render_template('sims.html', title='betapp - Simulation')
