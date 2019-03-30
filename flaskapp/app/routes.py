from flask import render_template, request
from app import app
from app.db import get_result_n_matches, get_fixture_n_matches

app.jinja_env.filters['zip'] = zip

@app.route('/')
@app.route('/about')
def index():
    return render_template('index.html', title='betapp - About')

@app.route('/tables')
def tables():
    page_fix = int(request.args.get('page_fix', 0))
    page_res = int(request.args.get('page_res', 0))
    n_fix = 6
    n_res = 6
    total_fix, fixtures = get_fixture_n_matches(n_fix, page_fix)
    total_res, results = get_result_n_matches(n_res, page_res)
    return render_template('tables.html', title='betapp - Tables', fixtures=fixtures, total_fix=total_fix,
                           page_fix=page_fix, n_fix=n_fix, results=results, total_res=total_res, page_res=page_res,
                           n_res=n_res)

@app.route('/sim')
def sim():
    return render_template('sims.html', title='betapp - Simulation')
