from typing import List

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
import plotly.express as px
from plotly.graph_objects import Figure, Heatmap, Layout, Scatter

from ..data_import import simulation_data
from ..static_elements import brand, footer
from ..layouts import fig_layout, main_graph_props, px_template
from ..simulation_files import NETWORKS, MODELS, ID_RRR, ID_P_VACC_INIT, \
    ID_P_VACC, ID_P_QUAR, VALS_MAPPING


# Factory and helper functions =====
def make_dropdown(label, dropdown_options, clearable=False, div_id=''):
    return html.Div([
        html.Label(label),
        dcc.Dropdown(**dropdown_options, clearable=clearable),
    ], id=div_id)


def make_slider(label, slider_options):
    return html.Div([
        html.Label([
            label,
            ': ',
            html.Span(
                id={'type': 'label', 'index': slider_options['id']['index']}
            )
        ]),
        dcc.Slider(**slider_options)
    ])


def make_heatmap(param, network):
    fig = Figure(data=Heatmap(z=[[1, 20, 30], [20, 1, 60], [30, 60, 1]]),
                 layout=Layout(template=px_template))

    fig.update_layout(**fig_layout)
    return fig


def make_waterfall(param, model, network, filters):
    df = filter_df(model, network, filters)
    epidemic_size = epidemic_size_per_param(df, param)
    fig = px.scatter(epidemic_size, x=param, y="epidemic_size", template=px_template)
    fig.update_layout(**fig_layout)
    return fig


def make_main_graph(df, grouped_df):

    fig_line = px.line(grouped_df, **main_graph_props)
    fig_line.update_layout(showlegend=False)

    fig_scat = px.scatter(df, **main_graph_props, template=px_template)
    fig_scat.update_layout(**fig_layout)

    fig = Figure(data=fig_line.data + fig_scat.data)

    return fig


def filter_df(model, network, filters):
    return simulation_data.subset_data(model, network, filters)


def df_group_mean(df):
    grouped = df.groupby(['time', 'compartment']).mean()
    grouped.reset_index(inplace=True)
    return grouped


def epidemic_size_per_param(df, param):

    time_max = df.groupby(['experiment_id', param]).agg(
        time_max=pd.NamedAgg(column='time', aggfunc='max')
    ).to_dict()['time_max']

    filtered = df[df.apply(
        lambda x: np.isclose(time_max[(x['experiment_id'], x[param])], x['time']) and
                  x['compartment'] in ['R', 'E'], axis=1)
    ]

    epidemic_size = filtered.groupby(
        ['experiment_id', param]
    ).value.sum()

    epidemic_size = epidemic_size.reset_index()
    epidemic_size.rename(columns={'value': 'epidemic_size'}, inplace=True)

    return epidemic_size[[param, 'epidemic_size']]


def make_detail_table_df(df):
    out = {}

    last_time = df[df.time == max(df.time)]

    out['total infected'] = calc_perc_infected(last_time)
    out['susceptible remaining'] = calc_susceptible_remaining(last_time)
    out['peak time'] = calc_peak_time(df)
    out['peak infected'] = calc_peak_infected(df)
    out['effective end'] = calc_effective_end(df)

    for k, v in out.items():
        out[k] = '%.4f' % v

    return pd.DataFrame({
        'key': list(out.keys()),
        'value': list(out.values())
    })


def make_detail_table(df):
    # todo use mean values for this...
    table_df = make_detail_table_df(df)
    return dbc.Table.from_dataframe(
        table_df, striped=True, bordered=True, hover=True, responsive=True,
        id='summary-data-table', className='table'
    )


def calc_perc_infected(df):
    r = df[df.compartment == 'R'].iloc[0]['value']
    e = df[df.compartment == 'E'].iloc[0]['value']
    return r + e


def calc_susceptible_remaining(df):
    return df[df.compartment == 'S'].iloc[0]['value']


def calc_peak_time(df):
    return df.loc[df[df.compartment == 'I'].value.idxmax(), 'time']


def calc_peak_infected(df):
    return df[df.compartment == 'I'].value.max()


def calc_effective_end(df):
    # first time, infected is sub 1% again
    # todo what threshold makes sense here?
    infected = df[df.compartment == 'I']

    idx = find_sub_threshold_after_peak(infected.value.tolist(), 0.01)

    if idx is None:
        return None

    return infected.time.values[idx]


def find_sub_threshold_after_peak(l: List, v: float):
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


# Create elements =====

model_dropdown = make_dropdown('Model', dict(
    id='model-dropdown',
    options=[{"label": m, "value": m} for m in MODELS],
    value=MODELS[0],
))

network_dropdown = make_dropdown('Network', dict(
    id='network-dropdown',
    options=[{"label": m, "value": m} for m in NETWORKS],
    value=NETWORKS[0],
))

quarantine_slider = make_slider(ID_P_QUAR, dict(
    id={'type': 'slider', 'index': ID_P_QUAR},
    **VALS_MAPPING[ID_P_QUAR], value=VALS_MAPPING[ID_P_QUAR]['min']))

vaccine_slider = make_slider(ID_P_VACC, dict(
    id={'type': 'slider', 'index': ID_P_VACC},
    **VALS_MAPPING[ID_P_VACC], value=VALS_MAPPING[ID_P_VACC]['min']))

vaccine_init_slider = make_slider(ID_P_VACC_INIT, dict(
    id={'type': 'slider', 'index': ID_P_VACC_INIT},
    **VALS_MAPPING[ID_P_VACC_INIT], value=VALS_MAPPING[ID_P_VACC_INIT]['min']))

rrr_slider = make_slider(ID_RRR, dict(
    id={'type': 'slider', 'index': ID_RRR},
    **VALS_MAPPING[ID_RRR], value=VALS_MAPPING[ID_RRR]['min']))

controls = dbc.Card([
    model_dropdown,
    network_dropdown,
    quarantine_slider,
    vaccine_slider,
    vaccine_init_slider,
    rrr_slider
], body=True, id='controls')

main_graph = dbc.Card([
    dbc.CardBody(
        dcc.Graph(id='epidemic-curve-graph', responsive=True)
    )
], id='main')

data_table = dbc.Card([
    dbc.CardBody(
        dbc.Table(),
        style={'overflowY': 'auto'},
        id='table-card-body'
    )
], id='table')

heatmap_tabs = dbc.Card(
    [
        dbc.CardHeader(
            dbc.Tabs(
                [
                    dbc.Tab(label=ID_P_QUAR, tab_id=ID_P_QUAR),
                    dbc.Tab(label=ID_P_VACC, tab_id=ID_P_VACC),
                    dbc.Tab(label=ID_P_VACC_INIT, tab_id=ID_P_VACC_INIT),
                    dbc.Tab(label=ID_RRR, tab_id=ID_RRR),
                ],
                id="heatmap-card-tabs",
                card=True,
                active_tab=ID_P_QUAR,
            )
        ),
        dbc.CardBody(
            dcc.Graph(id="heatmap-graph", responsive=True)
        )
    ],
    id='heatmap'
)

waterfall_tabs = dbc.Card(
    [
        dbc.CardHeader(
            dbc.Tabs(
                [
                    dbc.Tab(label=ID_P_QUAR, tab_id=ID_P_QUAR),
                    dbc.Tab(label=ID_P_VACC, tab_id=ID_P_VACC),
                    dbc.Tab(label=ID_P_VACC_INIT, tab_id=ID_P_VACC_INIT),
                    dbc.Tab(label=ID_RRR, tab_id=ID_RRR),
                ],
                id="waterfall-card-tabs",
                card=True,
                active_tab=ID_P_QUAR,
            )
        ),
        dbc.CardBody(
            dcc.Graph(id="waterfall-graph", responsive=True)
        )
    ],
    id='waterfall'
)

# Assemble components into page

index_page = [
    brand,
    controls,
    footer,
    main_graph,
    data_table,
    waterfall_tabs,
    heatmap_tabs
]
