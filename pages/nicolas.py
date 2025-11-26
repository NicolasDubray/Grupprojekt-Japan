import hashlib as hl
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import dash
from dash import html, dcc, callback, Input, Output

dash.register_page(__name__, path='/nicolas', name='Nicolas')

athlete_events = pd.read_csv(r'athlete_events.csv')

athlete_events_enc = athlete_events.copy()
athlete_events_enc['Name'] = athlete_events_enc['Name'].apply(lambda x: hl.sha256(x.encode()).hexdigest())
athlete_events_enc = athlete_events_enc.rename(columns={'Name': 'SHA-256-Name'})

events = athlete_events_enc[athlete_events_enc['NOC'] == 'JPN']

def fig_histogram(events, sport, start_year, end_year, title):
    events = events[
        (events['Sport'] == sport) &
        (events['Year'] >= start_year) &
        (events['Year'] <= end_year)
    ]

    events = events[~events['Event'].str.contains('Team', case=False, na=False)]

    events['Medalist'] = events['Medal'].notnull()

    medalists = events[events['Medalist']].copy()
    medalists['Group'] = 'Medalist'

    non_medalists = events[~events['Medalist']].copy()
    non_medalists['Group'] = 'Non-Medalist'

    athletes_concat = pd.concat([medalists, non_medalists])
    athletes_concat = athletes_concat.dropna(subset='Height')

    color_map = {"Non-Medalist": "red", "Medalist": "blue"}
    fig = px.histogram(athletes_concat,
        x='Height',
        color='Group',
        histnorm='density',
        barmode='overlay',
        marginal='violin',
        color_discrete_map=color_map,
        opacity=0.5)

    fig.update_layout(title=title, height=750)

    return fig

start_year = 1992
end_year = 2016
fig_boxing_jpn = fig_histogram(events, 'Boxing', start_year, end_year, 'Boxing')
fig_fencing_jpn = fig_histogram(events, 'Fencing', start_year, end_year, 'Fencing')
fig_judo_jpn = fig_histogram(events, 'Judo', start_year, end_year,  'Judo')
fig_taekwondo_jpn = fig_histogram(events, 'Taekwondo', start_year, end_year, 'Taekwondo')
fig_wrestling_jpn = fig_histogram(events, 'Wrestling', start_year, end_year, 'Wrestling')

low_physicality_sports = ['Fencing', 'Curling', 'Golf', 'Shooting', 'Equestrianism', 'Sailing', 'Archery']

events = athlete_events[athlete_events['Sport'].isin(low_physicality_sports)].copy()
events = events[~events['Event'].str.contains('Team', case=False, na=False)]
events = events[
    ~((events['Sport'] == 'Equestrianism') &
    ((events['Event'].str.contains('Eventing', case=False, na=False)) |
    (events['Event'].str.contains('Mixed', case=False, na=False))))
]

events['Sport'] = events['Sport'].replace({'Equestrianism': 'Equestrianism (no Eventing)'})

events = events.dropna(subset=['Medal'])
events = events.dropna(subset=['Age'])

fig_age_dist_low_physicality_sports = px.box(events,
    x='Sport',
    y='Age',
    points='all',
    hover_data=['Event', 'NOC', 'Medal', 'Year'],
    title="Age Distribution of Olympic Athletes in Individual Low-Physicality Sports (Global)")
fig_age_dist_low_physicality_sports.update_traces(marker=dict(size=2.5))

plots = {
    "Height Distribution of Japanese Athletes in Combat Sports": [
        (fig_boxing_jpn, "Height Distribution of Japanese Athletes in Boxing"),
        (fig_fencing_jpn, "Height Distribution of Japanese Athletes in Fencing"),
        (fig_judo_jpn, "Height Distribution of Japanese Athletes in Judo"),
        (fig_taekwondo_jpn, "Height Distribution of Japanese Athletes in Taekwondo"),
        (fig_wrestling_jpn, "Height Distribution of Japanese Athletes in Wrestling")
    ],
    "Age Distribution": [
        (fig_age_dist_low_physicality_sports, "Age Distribution of Olympic Athletes in Individual Low-Physicality Sports (Global)")
    ]
}

layout = html.Div([
    dcc.Dropdown(
        id={'page': 'nicolas', 'role': 'dropdown'},
        options=[{'label': key, 'value': key} for key in plots.keys()],
        value=list(plots.keys())[0]
    ),
    html.Div(id={'page': 'nicolas', 'role': 'plot-container'})
])
@callback(
    Output({'page': 'nicolas', 'role': 'plot-container'}, 'children'),
    Input({'page': 'nicolas', 'role': 'dropdown'}, 'value')
)
def update_graph(selected_plot):
    fig_title_pairs = plots[selected_plot]

    return [
        html.Div([
            html.H3(title, style={"text-align": "center"}),
            dcc.Graph(figure=fig)
        ])
        for fig, title in fig_title_pairs
    ]