# Example from https://dash.plotly.com/layout

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

external_stylesheets = [dbc.themes.SOLAR]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
df = pd.DataFrame({
    "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
    "Amount": [4, 1, 2, 2, 4, 5],
    "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
})

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "24rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "26rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

fig = px.bar(df, x="Fruit", y="Amount", color="City", barmode="group")

controls = dbc.Card(
    [
        dbc.FormGroup(
            [
                dbc.Label("X variable"),
                dcc.Dropdown(
                    id="x-variable",
                    options=[
                        {"label": col, "value": col} for col in df.columns
                    ],
                    value="sepal length (cm)",
                ),
            ]
        ),
        dbc.FormGroup(
            [
                dbc.Label("Y variable"),
                dcc.Dropdown(
                    id="y-variable",
                    options=[
                        {"label": col, "value": col} for col in df.columns
                    ],
                    value="sepal width (cm)",
                ),
            ]
        ),
        dbc.FormGroup(
            [
                dbc.Label("Cluster count"),
                dbc.Input(id="cluster-count", type="number", value=3),
            ]
        ),
    ],
    body=True,
)

sidebar = html.Div(
    [
        html.H2("EpiSim", className="display-4"),
        html.Hr(),
        html.P(
            "Epidemic simulations", className="lead"
        ),
        dbc.Nav(
            [
                dbc.NavLink("Home", href="/", active="exact"),
                dbc.NavLink("Page 1", href="/page-1", active="exact"),
                dbc.NavLink("Page 2", href="/page-2", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
        controls
    ],
    style=SIDEBAR_STYLE,
)

content = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id="cluster-graph1", figure=fig), md=4),
                dbc.Col(dcc.Graph(id="cluster-graph2", figure=fig), md=4),
            ],
            align="center",
            style={"margin-bottom": "2rem"}
        ),
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id="cluster-graph3", figure=fig), md=4),
                dbc.Col(dcc.Graph(id="cluster-graph4", figure=fig), md=4),
            ],
            align="center",
            style={"margin-bottom": "2rem"}
        ),
    ],
    fluid=True,
    style=CONTENT_STYLE,
    id="page-content"
)

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])


