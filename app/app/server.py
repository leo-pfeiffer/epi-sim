from typing import Union

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
from app.static_elements import brand, footer  # noqa
from app.layouts import fig_layout, fig_traces, px_line_props, table_layout  # noqa

import pandas as pd

external_stylesheets = [
    dbc.themes.SOLAR,
    'https://pro.fontawesome.com/releases/v5.10.0/css/all.css'
]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'EpiSim'

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
                                    columns=[],
                                    data=[],
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

# todo display graph metrics
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
    dcc.Location(id="url"), brand, content, footer
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
        out[net]['peak infected'] = calc_peak_infected(sub_df)
        out[net]['effective end'] = calc_effective_end(sub_df)

    # todo back and forth between dict and df is inefficient
    df_out = pd.DataFrame(out).reset_index().rename(columns={'index': ''})

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
    return df.loc[df[df.compartment == 'infected'].value.idxmax(), 'time']


def calc_peak_infected(df):
    return df[df.compartment == 'infected'].value.max()


def calc_effective_end(df):
    # first time, infected is sub 1% again
    # todo what threshold makes sense here?
    infected = df[df.compartment == 'infected']

    idx = find_sub_threshold_after_peak(infected.value.tolist(), 0.01)

    if idx is None:
        return None

    return infected.time.values[idx]


def find_sub_threshold_after_peak(l: list, v: float) -> Union[int, None]:
    """
    Find the index of the value in a list that is below a threshold  for the
    first time after a value above the peak. If the condition is not met for
    any values, return 0 if the first value of the list is below the threshold
    or None if the first value is above the threshold.
    :param l: List of values
    :param v: Threshold value
    :return: Index or None
    """
    for i in range(1, len(l)):
        if l[i - 1] > v >= l[i]:
            return i

    return 0 if l[0] <= v else None

