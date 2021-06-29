import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

import plotly.express as px
from app.cytoscape_graph import cyto_graph  # noqa
from app.data_import import seir_df, seivr_df  # noqa

external_stylesheets = [
    dbc.themes.SOLAR,
    'https://pro.fontawesome.com/releases/v5.10.0/css/all.css'
]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# df = seir_df.loc[seir_df.model == 'SEIR']
df = seivr_df.loc[seivr_df.model == 'SEIVR']

# df = pd.DataFrame({
#     "time": ([1, 2, 3, 4, 5] * 3) * 3,
#     "value": ([5, 4, 3, 2, 1] + [1, 3, 5, 4, 3] + [1, 2, 3, 4, 5]) * 3,
#     "compartment": (["S"] * 5 + ["I"] * 5 + ["R"] * 5) * 3,
#     "network": ["MN"] * 15 + ["PLC"] * 15 + ["PD"] * 15
# })


# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_WIDTH = 25
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": f"{SIDEBAR_WIDTH}%",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": f"{SIDEBAR_WIDTH}%",
    "width": f"{100 - SIDEBAR_WIDTH}%",
    "margin-right": "1rem",
    "padding": "1rem 1rem",
}

fig = px.line(df, x="time", y="value", color="compartment", facet_col="network",
              line_group="compartment", hover_name="compartment",
              template="plotly_white")

fig.update_traces(mode="lines", hovertemplate=None)

fig.update_layout(
    margin=dict(l=20, r=20, t=35, b=5),
    paper_bgcolor="#22444a",
    font_color="#839396",
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.25,
        xanchor="center",
        x=0.5
    ),
    hovermode="x unified"
)

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
        html.H2("EpiSim", className="display-4", id="app-name"),
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
        controls,
        html.Hr(),
        html.A(
            html.I(className="fab fa-github"),
            href="https://github.com/leo-pfeiffer/msc-thesis",
            style={"font-size": "2rem", "color": "#839496"}
        )
    ],
    style=SIDEBAR_STYLE,
    id="sidebar"
)

table_header = [
    html.Thead(html.Tr([html.Th("First Name"), html.Th("Last Name")]))
]

row1 = html.Tr([html.Td("Arthur"), html.Td("Dent")])
row2 = html.Tr([html.Td("Ford"), html.Td("Prefect")])
row3 = html.Tr([html.Td("Zaphod"), html.Td("Beeblebrox")])
row4 = html.Tr([html.Td("Trillian"), html.Td("Astra")])

table_body = [html.Tbody([row1, row2, row3, row4])]
table = dbc.Table(table_header + table_body, bordered=True)

content = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id="cluster-graph1", figure=fig), md=12),
            ],
            align="center",
            style={"margin-bottom": "2rem"}
        ),
        dbc.Row(
            [
                dbc.Col(dbc.Card([table], body=True), md=12),
            ],
            align="center",
            style={"margin-bottom": "2rem"}
        ),
        dbc.Row(
            [
                dbc.Col(cyto_graph, md=12)
            ],
            align="center",
            style={"margin-bottom": "1rem"}
        )
    ],
    fluid=False,
    style=CONTENT_STYLE,
    id="page-content"
)

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])
