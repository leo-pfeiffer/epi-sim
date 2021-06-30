import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_daq as daq
from dash.dependencies import Input, Output, State, MATCH, ALL
import plotly.express as px
import json

from app.cytoscape_graph import cyto_graph  # noqa
from app.data_import import data  # noqa
from app.static_elements import brand_narrow, brand_wide, footer  # noqa
from app.layouts import fig_layout, fig_traces, px_line_props, table_layout  # noqa

import pandas as pd

external_stylesheets = [
    dbc.themes.SOLAR,
    'https://pro.fontawesome.com/releases/v5.10.0/css/all.css'
]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'EpiSim'

table_df = pd.DataFrame(dict(
    key=['key1', 'key2', 'key3'],
    value=[1, 2, 3]
))

ctrls = []
figs = []
for k, v in data.items():
    # Controls
    ctrls.append(
        dbc.Row(
            [
                dbc.Col([
                    daq.BooleanSwitch(id=f'model-btn-{k}', style={'float': 'left'}, on=False),
                    dbc.Label(k.upper())
                ], md=4),
                dbc.Col([
                    dcc.Dropdown(
                        id=dict(
                            index=k,
                            type="network-checklist"
                        ),
                        options=[
                            {"label": net, "value": net} for net in v['networks']
                        ],
                        value=[],
                        multi=True
                    ),
                ], md=8)
            ]
        )
    )
    # Figures
    figs.append(
        dbc.Row(
            [dbc.Col(
                dbc.Card([
                    dbc.CardBody(dcc.Graph(id=dict(index=k, type="graph")),
                                 id=f'graph-card-{k}'),
                    dbc.CardFooter([
                        dbc.Button('Show details', id=f'show-details-{k}', n_clicks=0),
                        dbc.Collapse([
                            html.Hr(), dbc.Card([
                                dash_table.DataTable(
                                    id=dict(index=k, type="table"),
                                    columns=[{"name": i, "id": i} for i in table_df.columns],
                                    data=table_df.to_dict('records'),
                                    **table_layout
                                )
                            ], body=True)
                        ], id=f'details-{k}', is_open=False)
                    ]),
                ]), md=12),
            ],
            align="center",
            id=f"graph-row-{k}"
        ),
    )

controls = dbc.Card(ctrls, body=True)

graph_selector = dbc.Card(
    [
        dbc.ButtonGroup([dbc.Button(net) for net in ['MN_pre']])
    ]
)

controls_row = dbc.Row([dbc.Col(controls, md=12), html.P(id='output-value')], align='center')

graph_row = dbc.Row(
    [dbc.Col(dbc.Card(
        [dbc.CardHeader(graph_selector), dbc.CardBody(cyto_graph)], body=True), md=12)
    ],
    align="center"
)

content = dbc.Container(
    [controls_row] + figs + [graph_row],
    fluid=False,
    id="page-content"
)

app.layout = html.Div([
    dcc.Location(id="url"), brand_wide, brand_narrow, content, footer
])


# CALLBACKS ====
@app.callback(
    [Output(f'details-{k}', 'is_open') for k in data],
    [Output(f'show-details-{k}', 'n_clicks') for k in data],
    [Input(f"show-details-{k}", "n_clicks") for k in data],
    [State(f"details-{k}", "is_open") for k in data],
)
def toggle_details_visibility(*args):
    n = args[:len(args) // 2]
    is_open = args[len(args) // 2:]
    is_open_vals = []
    n_click_vals = [0] * (len(args) // 2)
    for i in range(len(n)):
        if n[i]:
            is_open_vals.append(not is_open[i])
        else:
            is_open_vals.append(is_open[i])

    return is_open_vals + n_click_vals


@app.callback(
    [Output(f'graph-row-{k}', 'style') for k in data],
    [Input(f'model-btn-{k}', 'on') for k in data]
)
def toggle_model_button(*args):
    styles = []
    for i, a in enumerate(args):
        if a:
            styles.append(dict())
        else:
            styles.append(dict(display='none'))
    return styles


@app.callback(
    Output({'type': 'graph', 'index': MATCH}, 'figure'),
    Output({'type': 'table', 'index': MATCH}, 'data'),
    Output({'type': 'table', 'index': MATCH}, 'columns'),
    Input({'type': 'network-checklist', 'index': MATCH}, 'value'),
    State({'type': 'graph', 'index': MATCH}, 'figure'),
)
def testing(networks, figure):

    ctx = dash.callback_context

    if ctx.triggered[0]['prop_id'] == '.':
        return {}, [], []

    if len(networks) == 0:
        return {}, [], []

    model = json.loads(ctx.triggered[0]['prop_id'].split('.')[0])['index']
    filtered_df = data[model]['df'][data[model]['df'].network.isin(networks)]

    fig = create_figure(filtered_df)
    dat, cols = create_detail_table(filtered_df)

    return fig, dat, cols


def create_figure(filtered_df):
    fig = px.line(filtered_df, **px_line_props)
    fig.update_traces(**fig_traces)
    fig.update_layout(**fig_layout)
    return fig


def create_detail_table(filtered_df):

    out = {}
    for net in filtered_df.network.unique().tolist():

        out[net] = dict()

        sub_df = filtered_df[filtered_df.network == net]
        last_time = sub_df[sub_df.time == max(sub_df.time)]

        out[net]['total infected'] = calc_perc_infected(last_time)
        out[net]['susceptible remaining'] = calc_susceptible_remaining(last_time)
        out[net]['peak time'] = calc_peak_time(sub_df)
        out[net]['effective end'] = calc_effective_end(sub_df)

    # todo back and forth between dict and df is inefficient
    #  also, naming the index column `.` is pretty stupid
    df_out = pd.DataFrame(out).reset_index().rename(columns={'index': '.'})

    columns = [{"name": i, "id": i} for i in df_out.columns]
    records = df_out.to_dict('records')

    return records, columns


def calc_perc_infected(df):
    r = df[df.compartment == 'removed'].iloc[0]['value']
    e = df[df.compartment == 'exposed'].iloc[0]['value']
    return r + e


def calc_susceptible_remaining(df):
    return df[df.compartment == 'susceptible'].iloc[0]['value']


def calc_peak_time(df):
    # todo
    return 100


def calc_effective_end(df):
    # todo (when is infected sub 1%? again)
    return 200
