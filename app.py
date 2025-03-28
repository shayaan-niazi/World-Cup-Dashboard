# Data handling
import pandas as pd
import pycountry

# Dash & Plotly
import dash
from dash import dcc, html, Input, Output
import plotly.express as px


# entering world cup data
data = [
    {"Year": 1930, "Winner": "Uruguay", "RunnerUp": "Argentina"},
    {"Year": 1934, "Winner": "Italy", "RunnerUp": "Czechoslovakia"},
    {"Year": 1938, "Winner": "Italy", "RunnerUp": "Hungary"},
    {"Year": 1950, "Winner": "Uruguay", "RunnerUp": "Brazil"},
    {"Year": 1954, "Winner": "Germany", "RunnerUp": "Hungary"},
    {"Year": 1958, "Winner": "Brazil", "RunnerUp": "Sweden"},
    {"Year": 1962, "Winner": "Brazil", "RunnerUp": "Czechoslovakia"},
    {"Year": 1966, "Winner": "England", "RunnerUp": "Germany"},
    {"Year": 1970, "Winner": "Brazil", "RunnerUp": "Italy"},
    {"Year": 1974, "Winner": "Germany", "RunnerUp": "Netherlands"},
    {"Year": 1978, "Winner": "Argentina", "RunnerUp": "Netherlands"},
    {"Year": 1982, "Winner": "Italy", "RunnerUp": "Germany"},
    {"Year": 1986, "Winner": "Argentina", "RunnerUp": "Germany"},
    {"Year": 1990, "Winner": "Germany", "RunnerUp": "Argentina"},
    {"Year": 1994, "Winner": "Brazil", "RunnerUp": "Italy"},
    {"Year": 1998, "Winner": "France", "RunnerUp": "Brazil"},
    {"Year": 2002, "Winner": "Brazil", "RunnerUp": "Germany"},
    {"Year": 2006, "Winner": "Italy", "RunnerUp": "France"},
    {"Year": 2010, "Winner": "Spain", "RunnerUp": "Netherlands"},
    {"Year": 2014, "Winner": "Germany", "RunnerUp": "Argentina"},
    {"Year": 2018, "Winner": "France", "RunnerUp": "Croatia"},
    {"Year": 2022, "Winner": "Argentina", "RunnerUp": "France"}
]

# creating a dataframe
df = pd.DataFrame(data)

# adding iso codes 
def get_iso(name):
    try:
        return pycountry.countries.lookup(name).alpha_3
    except:
        return None

df["Winner_ISO"] = df["Winner"].apply(get_iso)
df["RunnerUp_ISO"] = df["RunnerUp"].apply(get_iso)

df.head() 


# counting how many times each country has won
win_counts = df['Winner'].value_counts().reset_index()
win_counts.columns = ['Country', 'Wins']

# manually patching ISO codes for any countries pycountry can't handle
def get_iso_fixed(name):
    overrides = {
        "Czechoslovakia": "CZE"
    }
    if name in overrides:
        return overrides[name]
    try:
        return pycountry.countries.lookup(name).alpha_3
    except:
        return None

# applying fixed ISO function
win_counts['ISO'] = win_counts['Country'].apply(get_iso_fixed)

# setting up the dash app
app = dash.Dash(__name__)

# building the choropleth map
fig = px.choropleth(
    win_counts,
    locations='ISO',
    color='Wins',
    hover_name='Country',
    color_continuous_scale='Blues',
    title='FIFA World Cup Wins by Country'
)

# basic layout with just the map for now
app.layout = html.Div([
    html.H1("FIFA World Cup Dashboard", style={'textAlign': 'center'}),
    dcc.Graph(figure=fig)
])


# getting unique countries that have won
country_options = [{'label': country, 'value': country} for country in df['Winner'].unique()]

# adding a dropdown + output text under the map
app.layout = html.Div([
    html.H1("FIFA World Cup Dashboard", style={'textAlign': 'center'}),
    
    # world map
    dcc.Graph(figure=fig),

    # space between map and dropdown
    html.Br(),

    # country dropdown
    html.Label("Select a country to see how many times it has won:"),
    dcc.Dropdown(id='country-dropdown', options=country_options, value=None),

    # display win count
    html.Div(id='country-win-output', style={'marginTop': 20, 'fontWeight': 'bold'})
])


# getting unique countries that have won
country_options = [{'label': country, 'value': country} for country in df['Winner'].unique()]

# adding a dropdown + output text under the map
app.layout = html.Div([
    html.H1("FIFA World Cup Dashboard", style={'textAlign': 'center'}),
    
    # world map
    dcc.Graph(figure=fig),

    # space between map and dropdown
    html.Br(),

    # country dropdown
    html.Label("Select a country to see how many times it has won:"),
    dcc.Dropdown(id='country-dropdown', options=country_options, value=None),

    # display win count
    html.Div(id='country-win-output', style={'marginTop': 20, 'fontWeight': 'bold'})
])


# callback to update the win count when a country is selected
@app.callback(
    Output('country-win-output', 'children'),
    Input('country-dropdown', 'value')
)
def update_win_count(selected_country):
    if selected_country is None:
        return ""
    
    wins = df[df['Winner'] == selected_country].shape[0]
    return f"{selected_country} has won the World Cup {wins} time(s)."


# dropdown options for years (sorted oldest to newest)
year_options = [{'label': str(year), 'value': year} for year in sorted(df['Year'].unique())]

# update layout to include year dropdown + output
app.layout = html.Div([
    html.H1("FIFA World Cup Dashboard", style={'textAlign': 'center'}),

    # choropleth map
    dcc.Graph(figure=fig),

    html.Br(),

    # country win count section
    html.Label("Select a country to see how many times it has won:"),
    dcc.Dropdown(id='country-dropdown', options=country_options, value=None),
    html.Div(id='country-win-output', style={'marginTop': 20, 'fontWeight': 'bold'}),

    html.Br(),

    # year selector
    html.Label("Select a year to view the final result:"),
    dcc.Dropdown(id='year-dropdown', options=year_options, value=None),
    html.Div(id='year-result-output', style={'marginTop': 20, 'fontWeight': 'bold'})
])


# callback for year dropdown — shows winner and runner-up for selected year
@app.callback(
    Output('year-result-output', 'children'),
    Input('year-dropdown', 'value')
)
def show_final_result(selected_year):
    if selected_year is None:
        return ""
    
    row = df[df['Year'] == selected_year]
    if row.empty:
        return "No data for that year."

    winner = row.iloc[0]['Winner']
    runner_up = row.iloc[0]['RunnerUp']
    return f"In {selected_year}, {winner} won the World Cup. Runner-up: {runner_up}."

# run the Dash app (will open in a browser)
import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8050))
    app.run(host='0.0.0.0', port=port, debug=True)

