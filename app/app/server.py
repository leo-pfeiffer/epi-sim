import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

import plotly.express as px
from app.cytoscape_graph import cyto_graph  # noqa
from app.data_import import seir_df, seivr_df  # noqa
from app.sidebar import brand_narrow, brand_wide  # noqa

external_stylesheets = [
    dbc.themes.SOLAR,
    'https://pro.fontawesome.com/releases/v5.10.0/css/all.css'
]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# df = seir_df.loc[seir_df.model == 'SEIR']
df = seivr_df.loc[seivr_df.model == 'SEIVR']

networks = df.network.unique().tolist()
models = df.model.unique().tolist()

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
                dbc.Label("Networks"),
                dcc.Checklist(
                    id="check-networks",
                    labelClassName="checklist-option",
                    options=[
                        {"label": net, "value": net} for net in networks
                    ],
                    value=networks[0],
                ),
            ]
        ),
        dbc.FormGroup(
            [
                dbc.Label("Models"),
                dcc.Checklist(
                    id="check-models",
                    labelClassName="checklist-option",
                    options=[
                        {"label": mod, "value": mod} for mod in models
                    ],
                    value=models[0],
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


table_header = [
    html.Thead(html.Tr([html.Th("First Name"), html.Th("Last Name")]))
]

row1 = html.Tr([html.Td("Arthur"), html.Td("Dent")])
row2 = html.Tr([html.Td("Ford"), html.Td("Prefect")])
row3 = html.Tr([html.Td("Zaphod"), html.Td("Beeblebrox")])
row4 = html.Tr([html.Td("Trillian"), html.Td("AstraZeneca")])

table_body = [html.Tbody([row1, row2, row3, row4])]
table = dbc.Table(table_header + table_body, bordered=True)

content = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(controls, md=12),
            ],
            align="center",
        ),
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id="cluster-graph1", figure=fig), md=12),
            ],
            align="center",
        ),
        dbc.Row(
            [
                dbc.Col(dbc.Card([table], body=True), md=12),
            ],
            align="center",
        ),
        dbc.Row(
            [
                dbc.Col(cyto_graph, md=12)
            ],
            align="center",
        )
    ],
    fluid=False,
    id="page-content"
)

app.layout = html.Div([dcc.Location(id="url"), brand_wide, brand_narrow, content])
