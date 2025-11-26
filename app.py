import dash
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, use_pages=True)
from pages import matteo, nicolas, niklas

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

app.layout = html.Div([
    html.Div(
        html.Img(
            src="/assets/japan_bg.png",
            style={'width': '300px'}
        ),
        style={'display': 'flex', 'justify-content': 'right'}
    ),

    dcc.Tabs(
        id="page-tabs",
        value="/matteo",
        children=[
            dcc.Tab(label="Matteo", value="/matteo"),
            dcc.Tab(label="Nicolas", value="/nicolas"),
            dcc.Tab(label="Niklas", value="/niklas")
        ]
    ),

    html.Div(id="tab-content")
])

@app.callback(
    Output("tab-content", "children"),
    Input("page-tabs", "value")
)
def render_tab(tab_value):
    for page in dash.page_registry.values():
        if page["path"] == tab_value:
            return page["layout"]
    return html.Div("Page not found")

if __name__ == "__main__":
    app.run(debug=True)