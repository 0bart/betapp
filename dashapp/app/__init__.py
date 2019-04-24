import dash

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
                                                                     
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.config.requests_pathname_prefix = app.config.routes_pathname_prefix.split('/')[-1]

server = app.server

from app import dashapp
from app import db
