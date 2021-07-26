import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
import plotly.express as px
from plotly.graph_objects import Figure, Heatmap, Layout

from ..data_processing import SimulationData
from ..static_elements import brand, footer, modal, toast
from ..layouts import fig_layout, main_graph_props, px_template
from ..simulation_files import NETWORKS, MODELS, ID_RRR, ID_P_VACC_INIT, \
    ID_P_VACC, ID_P_QUAR, VALS_MAPPING


# Load data set ==========
simulation_data = SimulationData()


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


def make_heatmap(param, network, model_filters):
    vm = VALS_MAPPING[param]
    x = np.arange(vm['min'], vm['max'], vm['step'])

    y = list(model_filters.keys())
    z = []

    # todo this is a bit slow....
    for m, f in model_filters.items():
        df = filter_df(m, network, f)
        epi = SimulationData.epidemic_size_per_param(df, param)
        epi = epi.groupby(param).mean()
        epi.sort_index(inplace=True)
        z.append(list(epi.epidemic_size.values))

    fig = Figure(
        data=Heatmap(
            z=z, x=x, y=y,
            colorscale=[[0, 'rgb(237, 198, 48)'], [1, 'rgb(5, 38, 150)']]
        ),
        layout=Layout(template=px_template)
    )

    fig.update_layout(**fig_layout)
    return fig


def make_waterfall(param, model, network, filters):
    df = filter_df(model, network, filters)
    epidemic_size = SimulationData.epidemic_size_per_param(df, param)
    fig = px.scatter(epidemic_size, x=param, y="epidemic_size", template=px_template)
    fig.update_layout(**fig_layout)
    return fig


def make_main_graph(df, grouped_df):
    fig_line = px.line(grouped_df, **main_graph_props)
    fig_scat = px.scatter(df, **main_graph_props, template=px_template)
    fig_scat.update_traces(showlegend=False, hoverinfo='none')

    fig = Figure(data=fig_line.data + fig_scat.data,
                 layout=Layout(template=px_template))

    fig.update_layout(**fig_layout)

    return fig


def filter_df(model, network, filters):
    return simulation_data.subset_data(model, network, filters)


def make_detail_table_df(df):
    out = {}

    last_time = df[df.time == max(df.time)]

    out['total infected'] = SimulationData.calc_perc_infected(last_time)
    out['susceptible remaining'] = SimulationData.calc_susceptible_remaining(last_time)
    out['peak time'] = SimulationData.calc_peak_time(df)
    out['peak infected'] = SimulationData.calc_peak_infected(df)
    out['effective end'] = SimulationData.calc_effective_end(df)

    for k, v in out.items():
        out[k] = '%.4f' % v

    return pd.DataFrame({
        'key': list(out.keys()),
        'value': list(out.values())
    })


def make_detail_table(df):
    table_df = make_detail_table_df(df)
    return dbc.Table.from_dataframe(
        table_df, striped=True, bordered=True, hover=True, responsive=True,
        id='summary-data-table', className='table'
    )


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
    modal,
    toast,
    controls,
    footer,
    main_graph,
    data_table,
    waterfall_tabs,
    heatmap_tabs
]
