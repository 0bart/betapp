import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go

from datetime import datetime, timedelta

from db import get_last_n_matches_for_plot 
import json

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

app.layout = html.Div(children=[
    dcc.DatePickerRange(id="dates",
                        min_date_allowed=datetime(2019, 1, 1),
                        max_date_allowed=datetime.today(),
                        start_date=datetime.today() - timedelta(days=30),
                        end_date=datetime.today()
                        ),
    html.Div([
        html.Div([
            html.Label('Base bid?', htmlFor="bid_base"),
            dcc.Input(id="bid_base", value=50, type="number")
        ], style={'display': 'block'}),
        html.Div([
            html.Label('# matches?', htmlFor="n"),
            dcc.Input(placeholder='How many matches?', id="n", value=10, type="number")
        ], style={'display': 'block'}),
        html.Div([
            html.Label('Bid type', htmlFor="bid_type"),
            dcc.Dropdown(id="bid_type", options=[{'label': "Flat", 'value': "flat"},
                                                 {'label': "Kelly criterium", 'value': "kelly_crit"}], value="flat")
        ], style={'display': 'block', 'min-width': '10vw'})
    ], style={'display': 'flex', 'flex-direction': 'row'}),
    dcc.Graph(id="main-graph")
])

@app.callback(
    Output('main-graph', 'figure'),
    [Input('n', 'value'),
     Input('bid_type', 'value'),
     Input('bid_base', 'value'),
     Input('dates', 'start_date'),
     Input('dates', 'end_date')])
def update_figure(n, bid_type, bid_base, start_date, end_date):
    #with open('MOCK_DATA.json') as infile:
    #    data = json.load(infile)

    print(start_date, end_date)
    #X, Y, text = gather_data_for_plot(data, n, bid_type, bid_base)
    X, Y, text = get_last_n_matches_for_plot(n, bid_base, bid_type)

    return {
        'data': [go.Scatter(
            x=X,
            y=Y,
            text=text,
            mode='lines+markers',
            line={
                'width': 2
            },
            marker={
                'size': 5,
                'opacity': 0.7,
            }
        )],
        'layout': go.Layout(
            xaxis={
                'title': "Match #",
                'type': 'linear'
            },
            yaxis={
                'title': "Cash",
                'type': 'linear'
            },
            hovermode='closest'
        )
    }

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=5050)
