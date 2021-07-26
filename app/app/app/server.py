import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, MATCH, ALL, ClientsideFunction, \
    State

from .simulation_files import PARAM_MAPPING

# page utils
from .pages.index import make_main_graph, make_detail_table, \
    make_heatmap, make_waterfall, filter_df

from .data_processing import SimulationData

# pages
from .pages import *

FONT_AWESOME = 'https://pro.fontawesome.com/releases/v5.10.0/css/all.css'

external_stylesheets = [
    dbc.themes.LUX,
    dbc.themes.LUX,
    FONT_AWESOME,
]

# suppress callback exceptions since we have multiple pages
app = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    suppress_callback_exceptions=True,
    title='EpiSim'
)

# Base layout
app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    html.Div(id='page'),
    html.Div(id="blank_output")
], id='page-content')


# CALLBACKS ====
@app.callback(
    [
        Output('epidemic-curve-graph', 'figure'),
        Output('table-card-body', 'children'),
        Output({'type': 'slider', 'index': ALL}, 'disabled'),
    ],
    [
        Input('model-dropdown', 'value'),
        Input('network-dropdown', 'value'),
        Input({'type': 'slider', 'index': ALL}, 'value')
     ],
)
def graph_callback(mod, net, sliders):

    ctx = dash.callback_context

    sliders_out = [x['id']['index'] for x in ctx.outputs_list[2]]
    slider_disabled = [
        not PARAM_MAPPING[mod][slider] for slider in sliders_out
    ]

    sliders_states = ctx.inputs_list[2]

    filters = {}
    for slider in sliders_states:
        idx = slider['id']['index']
        if PARAM_MAPPING[mod][idx]:
            filters[idx] = slider['value']

    df = filter_df(mod, net, filters)
    grouped = SimulationData.df_group_mean(df)
    fig = make_main_graph(df, grouped)

    table = make_detail_table(grouped)

    return fig, table, slider_disabled


@app.callback(
    Output({'type': 'label', 'index': MATCH}, 'children'),
    Input({'type': 'slider', 'index': MATCH}, 'value')
)
def slider_callback(value):
    return value


@app.callback(
    Output("waterfall-graph", "figure"),
    [
        Input("waterfall-card-tabs", "active_tab"),
        Input('model-dropdown', 'value'),
        Input('network-dropdown', 'value'),
        Input({'type': 'slider', 'index': ALL}, 'value')
    ]
)
def waterfall_tabs(active_tab, mod, net, slider_values):

    if not PARAM_MAPPING[mod][active_tab]:
        return {}

    ctx = dash.callback_context
    sliders_states = ctx.inputs_list[3]

    filters = {}
    for slider in sliders_states:
        idx = slider['id']['index']
        if PARAM_MAPPING[mod][idx] and idx != active_tab:
            filters[idx] = slider['value']

    return make_waterfall(active_tab, mod, net, filters)


@app.callback(
    Output("heatmap-graph", "figure"),
    [
        Input("heatmap-card-tabs", "active_tab"),
        Input('network-dropdown', 'value'),
        Input({'type': 'slider', 'index': ALL}, 'value')
    ]
)
def heatmap_tabs(active_tab, network, slider_values):

    ctx = dash.callback_context
    sliders_states = ctx.inputs_list[2]

    # models to include in heatmap
    model_filters = {}
    for k, v in PARAM_MAPPING.items():
        if v[active_tab]:
            model_filters[k] = {}

    # filters to apply per model
    for k in model_filters:
        for slider in sliders_states:
            idx = slider['id']['index']
            if PARAM_MAPPING[k][idx] and idx != active_tab:
                model_filters[k][idx] = slider['value']

    return make_heatmap(active_tab, network, model_filters)


# Update the index
@app.callback(
    Output('page', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/':
        return index_page
    elif pathname == '/model':
        return model_page
    elif pathname == '/data':
        return data_page
    elif pathname == '/about':
        return about_page
    else:
        return not_found_page


# Toogle modal
@app.callback(
    Output("help-modal", "is_open"),
    [Input("help-button", "n_clicks"),
     Input("close", "n_clicks")],
    [State("help-modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


# Client side callbacks ====
app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='switchStylesheet'
    ),
    Output('blank_output', 'style'),
    Input('url', 'pathname')
)
