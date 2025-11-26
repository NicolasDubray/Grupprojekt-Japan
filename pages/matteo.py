import hashlib as hl
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import html, dcc, callback, Input, Output

dash.register_page(__name__, path='/matteo', name='Matteo')

# load data
df = pd.read_csv(r'athlete_events.csv')

# SHA-256
df['Name_h'] = df['Name'].apply(
    lambda name: 
        hl.sha256(str(name).encode('utf-8')).hexdigest()
)

# masking and filtering 
japan_medals = df[(df['Team'].str.contains('Japan', case=False, na=False)) & (df['Medal'].notna())]
medal_count = len(japan_medals) 

# Japan's best 3 sports
top3 = japan_medals['Sport'].value_counts().head(3).reset_index()
top3.columns = ['Sport', 'Count']

# Japan's medals over the years
japan_summer = japan_medals[japan_medals['Season'] == 'Summer']
japan_winter = japan_medals[japan_medals['Season'] == 'Winter']

# count medals per year **GEMINI 3.0**
summer_year = japan_summer['Year'].value_counts().sort_index().reset_index()
winter_year = japan_winter['Year'].value_counts().sort_index().reset_index()
summer_year.columns = ['Year', 'Count']
winter_year.columns = ['Year', 'Count']


# Japan's athletes age 
Japan_age = df[(df['Team'].str.contains('Japan', case=False, na=False)) &
               (df['Age'].notna())]

# Japan's medals in 4 sports
sports_list = ['Gymnastics', 'Swimming', 'Ski Jumping', 'Speed Skating']
japan_sport_medals = japan_medals[japan_medals['Sport'].isin(sports_list)]
medals_by_sport = japan_sport_medals['Sport'].value_counts()
detailed_medals = japan_sport_medals.groupby(['Sport', 'Medal']).size()


# size and weight over time
japan_athletes = df[df['Team'].str.contains('Japan', case=False, na=False)]

size_weight_time = japan_athletes.groupby('Year').agg({
    'Height': 'mean',
    'Weight': 'mean'
}).dropna()

# gender in sports_list
medals_by_sex = japan_sport_medals.groupby(['Sport', 'Sex']).size().reset_index(name='Count')

# where Japan won medals
city_medals = japan_medals.groupby('City').size().reset_index(name='Medal_Count')

# PLOTS
# top3 sports barplot
fig_top3 = px.bar(
    top3, x='Sport', y='Count',
    title='Top 3 Sports',
    color_discrete_sequence=['#FF0000']
)

# medals summer OS lineplot
fig_year = px.line(
    summer_year, x='Year', y='Count',
    title='Japan Medals per Year (Summer)',
    markers=True,
    color_discrete_sequence=['#FFD700']
)

# medals winter OS lineplot
fig_year_winter = px.line(
    winter_year, x='Year', y='Count',
    title='Japan Medals per Year (Winter)',
    markers=True,
    color_discrete_sequence=['#0066FF']
)

# age distribution in OS histogram
fig_age = px.histogram(
    Japan_age, x='Age', nbins=20,
    title='Age Distribution of Japanese Athletes',
    color_discrete_sequence=['#FF00FF']
)

# plot medals distribution piechart **DEEPSEEK**
fig_medals_sports = make_subplots(
    rows=1, cols=4,
    subplot_titles=sports_list,
    specs=[[{'type': 'pie'}, {'type': 'pie'}, {'type': 'pie'}, {'type': 'pie'}]]
)
for i, sport in enumerate(sports_list):
    sport_data = japan_sport_medals[japan_sport_medals['Sport'] == sport]
    medal_counts = sport_data['Medal'].value_counts()
    
    fig_medals_sports.add_trace(
        go.Pie(
            labels=medal_counts.index,
            values=medal_counts.values,
            name=sport,
            marker_colors=['#FFD700', '#C0C0C0', '#CD7F32']
        ),
        row=1, col=i+1
    )

fig_medals_sports.update_layout(
    title_text='Japan Medal Distribution by Sport',
    title_x=0.5,
    height=500
)

# number of medals weight VS height
four_sports_data = df[
    (df['Team'].str.contains('Japan', case=False, na=False)) & 
    (df['Sport'].isin(sports_list)) &
    (df['Height'].notna()) & 
    (df['Weight'].notna())
]

# gender division per sport barplot
fig_gender_sports = px.bar(
    medals_by_sex,
    x='Sport',
    y='Count',
    color='Sex',
    title='Japan Medal Breakdown by Sport and Gender',
    color_discrete_map={'M': '#0066FF', 'F': '#FF00FF'},
    template='plotly_white'
)
fig_gender_sports.update_layout(
    title_x=0.5,
    legend_title_text='Gender',
    xaxis_title='Sport',
    yaxis_title='Total Medal Count',
    hovermode='x unified',
    xaxis={
        'categoryorder': 'array',
        'categoryarray': sports_list 
    }
)

# weight vs height heatmap
fig_weight_height = px.density_heatmap(
    four_sports_data,
    x='Height',
    y='Weight',
    title='Weight vs Height in Japanese Athletes (Top 4 Sports)',
    color_continuous_scale=['#150048', '#8C008C', '#FF8000', '#FF0000']  
)

# weight vs height in time lineplot
fig_physique = px.line(size_weight_time.reset_index(), 
              x='Year', 
              y=['Height', 'Weight'],
              title='Japanese Athletes Physique Over Time',
              color_discrete_sequence=['#a56814', '#311906'],
              labels={'value': 'Measurement (cm/kg)', 'variable': 'Measurement Type'}
)
fig_physique.for_each_trace(lambda t: t.update(name='Height' if t.name=='Height' else 'Weight'))

# age vs medals scatterplot
medal_athletes = four_sports_data[four_sports_data['Medal'].notna()]
fig_age_medals = px.scatter(
    medal_athletes,
    x='Age',
    color='Sport',
    title='Age vs Medals Won for Japanese Athletes (Top 4 Sports)',
    hover_data=['Name', 'Year', 'Medal'],
    color_discrete_sequence=['#66c2a5', '#fc8d62', '#8da0cb', '#e78ac3'] 
)

summer = go.Figure

plots = {
    'sports': fig_top3,
    'summer': fig_year, 
    'winter': fig_year_winter,
    'age': fig_age,
    'medals_sport': fig_medals_sports,
    'medals_gender': fig_gender_sports,
    'weight_height': fig_weight_height,
    'physique': fig_physique,
    'age_medals': fig_age_medals
}

layout = html.Div([
    dcc.Dropdown(
        id={'page': 'matteo', 'role': 'dropdown'},
        options=[{'label': key, 'value': key} for key in plots.keys()],
        value=list(plots.keys())[0]
    ),
    dcc.Graph(id={'page': 'matteo', 'role': 'plot'})
])

@callback(
    Output({'page': 'matteo', 'role': 'plot'}, 'figure'),
    Input({'page': 'matteo', 'role': 'dropdown'}, 'value')
)
def update_graph(selected_plot):
    return plots[selected_plot]