import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, MATCH, ALL, ClientsideFunction, \
    State

from .simulation_files import PARAM_MAPPING, NETWORK_MAPPING
from .data_processing import SimulationData

# pages
from .pages import *

# configure logging
from .log_config import config_logger

config_logger()

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

# show only networks available for selected disease
@app.callback(
    [
        Output('network-dropdown', 'options'),
        Output('network-dropdown', 'value'),
    ],
    [Input('disease-dropdown', 'value')],
    [State('network-dropdown', 'value')]
)
def available_networks(disease, network):

    available = NETWORK_MAPPING[disease]
    options = [{'label': x, 'value': x} for x in available]
    value = network if network in available else available[0]

    return options, value


# creates the main figures from the control bar selection
@app.callback(
    [
        Output('epidemic-curve-graph', 'figure'),
        Output('table-card-body', 'children'),
        Output({'type': 'slider', 'index': ALL}, 'disabled'),
    ],
    [
        Input('disease-dropdown', 'value'),
        Input('model-dropdown', 'value'),
        Input('network-dropdown', 'value'),
        Input({'type': 'slider', 'index': ALL}, 'value')
    ],
)
def main_graph_callback(disease, mod, net, sliders):
    ctx = dash.callback_context

    # based on model selection, enable or disable sliders
    sliders_out = [x['id']['index'] for x in ctx.outputs_list[2]]
    slider_disabled = [
        not PARAM_MAPPING[mod][slider] for slider in sliders_out
    ]

    sliders_states = ctx.inputs_list[3]

    # get the slider settings and use them as filters
    filters = {}
    for slider in sliders_states:
        idx = slider['id']['index']
        if PARAM_MAPPING[mod][idx]:
            filters[idx] = slider['value']

    # save current selected state
    index.simulation_data.current_state = {
        'disease': disease,
        'model': mod,
        'network': net,
        'filters': filters
    }

    df = index.filter_df(disease, mod, net, filters)
    df = SimulationData.fill_experiment_length_gap(df)
    grouped = SimulationData.df_group_mean(df)
    fig = index.make_main_graph(df, grouped)

    table = index.make_detail_table(grouped)

    return fig, table, slider_disabled


@app.callback(
    Output({'type': 'label', 'index': MATCH}, 'children'),
    Input({'type': 'slider', 'index': MATCH}, 'value')
)
def slider_callback(value):
    return value


# create the scatter plot
@app.callback(
    Output("waterfall-graph", "figure"),
    [
        Input("waterfall-card-tabs", "active_tab"),
        Input('model-dropdown', 'value'),
        Input('network-dropdown', 'value'),
        Input('disease-dropdown', 'value'),
        Input({'type': 'slider', 'index': ALL}, 'value')
    ]
)
def waterfall_tabs(active_tab, mod, net, disease, slider_values):
    if not PARAM_MAPPING[mod][active_tab]:
        return {}

    ctx = dash.callback_context
    sliders_states = ctx.inputs_list[4]

    filters = {}
    for slider in sliders_states:
        idx = slider['id']['index']
        if PARAM_MAPPING[mod][idx] and idx != active_tab:
            filters[idx] = slider['value']

    return index.make_waterfall(active_tab, mod, net, disease, filters)


# create the heatmap figure
@app.callback(
    Output("heatmap-graph", "figure"),
    [
        Input("heatmap-card-tabs", "active_tab"),
        Input('network-dropdown', 'value'),
        Input('disease-dropdown', 'value'),
        Input({'type': 'slider', 'index': ALL}, 'value')
    ]
)
def heatmap_tabs(active_tab, network, disease, slider_values):
    ctx = dash.callback_context
    sliders_states = ctx.inputs_list[3]

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

    return index.make_heatmap(active_tab, network, disease, model_filters)


# Validation graphs
@app.callback(
    [Output('total-cases-graph', 'figure'),
     Output('new-cases-graph', 'figure')],
    Input('validation-dropdown', 'value')
)
def update_validation_graphs(name):
    tc_fig = validation.make_total_case_plot(name)
    nc_fig = validation.make_new_case_plot(name)
    return tc_fig, nc_fig


# Update the index
@app.callback(
    Output('page', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/':
        return index_page
    elif pathname == '/validation':
        return validation_page
    elif pathname == '/model':
        return model_page
    elif pathname == '/data':
        return data_page
    elif pathname == '/about':
        return about_page
    else:
        return not_found_page


# Toggle modal
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


# Download data set
@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("btn_csv", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    # get state
    state = index.simulation_data.current_state

    # apply filters
    df = index.filter_df(
        state['disease'], state['model'], state['network'], state['filters']
    )

    return dcc.send_data_frame(df.to_csv, "simulation_results.csv")


# Client side callbacks ====
app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='switchStylesheet'
    ),
    Output('blank_output', 'style'),
    Input('url', 'pathname')
)
