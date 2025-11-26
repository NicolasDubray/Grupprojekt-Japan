import hashlib as hl
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import html, dcc, callback, Input, Output

dash.register_page(__name__, path='/mans', name='Måns')

temp = go.Figure

plots = {
    'temp': temp
}

layout = html.Div([
    dcc.Dropdown(
        id={'page': 'mans', 'role': 'dropdown'},
        options=[{'label': key, 'value': key} for key in plots.keys()],
        value=list(plots.keys())[0]
    ),
    dcc.Graph(id={'page': 'mans', 'role': 'plot'})
])

@callback(
    Output({'page': 'mans', 'role': 'plot'}, 'figure'),
    Input({'page': 'mans', 'role': 'dropdown'}, 'value')
)
def update_graph(selected_plot):
    return plots[selected_plot]