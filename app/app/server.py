import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, MATCH

from .data_import import data
from .static_elements import brand, footer
from .layouts import table_layout
from .factory import make_dropdown, make_slider, create_detail_table

from .layouts import fig_layout, fig_traces, px_line_props
import plotly.express as px
from plotly.graph_objects import Figure, Heatmap

FONT_AWESOME = 'https://pro.fontawesome.com/releases/v5.10.0/css/all.css'

external_stylesheets = [
    dbc.themes.SOLAR,
    dbc.themes.SOLAR,
    FONT_AWESOME,
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'EpiSim'


model_dropdown = make_dropdown('Model', dict(
    id='model-dropdown',
    options=[{"label": m, "value": m} for m in data.keys()],
    value=list(data.keys())[0],
))

network_dropdown = make_dropdown('Network', dict(
    id='network-dropdown',
    options=[{"label": m, "value": m} for m in data.keys()],
    value=list(data.keys())[0],
))

quarantine_slider = make_slider('P_QUARANTINE', dict(
    id={'type': 'slider', 'index': 'p-quarantine'}, min=0, max=1, step=0.1, value=0))

vaccine_slider = make_slider('P_VACCINE', dict(
    id={'type': 'slider', 'index': 'p-vaccine'}, min=0, max=1, step=0.1, value=0))

vaccine_init_slider = make_slider('P_VACCINE_INIT', dict(
    id={'type': 'slider', 'index': 'p-vaccine-init'}, min=0, max=1, step=0.1, value=0))

rrr_slider = make_slider('RRR', dict(
    id={'type': 'slider', 'index': 'rrr'}, min=0, max=1, step=0.1, value=0))

ctrls = [model_dropdown, network_dropdown, quarantine_slider, vaccine_slider,
         vaccine_init_slider, rrr_slider]

controls = dbc.Card(ctrls, body=True, id='controls')

main_graph = dbc.Card([
    dbc.CardBody([dcc.Graph(id='my-graph', responsive=True)])
], id='main')

data_table = dbc.Card([
    dash_table.DataTable(
        id='my-table',
        columns=[],
        data=[], **table_layout)
], body=True, id='table')

heatmap_tabs = dbc.Card(
    [
        dbc.CardHeader(
            dbc.Tabs(
                [
                    dbc.Tab(label="Tab 1", tab_id='tab-1'),
                    dbc.Tab(label="Tab 2", tab_id='tab-2'),
                ],
                id="heatmap-card-tabs",
                card=True,
                active_tab="tab-1",
            )
        ),
        dbc.CardBody(dcc.Graph(id="heatmap-figure", responsive=True))
    ],
    id='heatmap'
)

waterfall_tabs = dbc.Card(
    [
        dbc.CardHeader(
            dbc.Tabs(
                [
                    dbc.Tab(label="Tab 1", tab_id='tab-1'),
                    dbc.Tab(label="Tab 2", tab_id='tab-2'),
                ],
                id="waterfall-card-tabs",
                card=True,
                active_tab="tab-1",
            )
        ),
        dbc.CardBody(dcc.Graph(id="waterfall-figure", responsive=True))
    ],
    id='waterfall'
)

app.layout = html.Div([
    dcc.Location(id="url"), brand, controls, footer, main_graph, data_table, waterfall_tabs, heatmap_tabs, html.Div(id="blank_output")
], id="page")


# CALLBACKS ====
@app.callback(
    Output('my-graph', 'figure'),
    Output('my-table', 'data'),
    Output('my-table', 'columns'),
    Input('model-dropdown', 'value'),
    Input('network-dropdown', 'value')
)
def graph_callback(model, network):

    network = 'MN_pre'

    filtered_df = data[model]['df'][data[model]['df'].network == network]

    fig = px.line(filtered_df, **px_line_props)
    fig.update_traces(**fig_traces)
    fig.update_layout(**fig_layout)

    dat, cols = create_detail_table(filtered_df)

    return fig, dat, cols


@app.callback(
    Output({'type': 'label', 'index': MATCH}, 'children'),
    Input({'type': 'slider', 'index': MATCH}, 'value')
)
def slider_callback(value):
    return value


@app.callback(
    Output("waterfall-figure", "figure"),
    Input("waterfall-card-tabs", "active_tab")
)
def waterfall_tabs(active_tab):
    df = px.data.iris()
    fig = px.scatter(df, x="sepal_width", y="sepal_length")
    fig.update_layout(**fig_layout)
    return fig


@app.callback(
    Output("heatmap-figure", "figure"),
    Input("heatmap-card-tabs", "active_tab")
)
def heatmap_tabs(active_tab):
    fig = Figure(data=Heatmap(
        z=[[1, 20, 30],
           [20, 1, 60],
           [30, 60, 1]]))

    fig.update_layout(**fig_layout)
    return fig


# Just for fun: Change the theme of the app
# Source: https://github.com/AnnMarieW/HelloDash/blob/main/app.py
app.clientside_callback(
    """
    function(url) {
        // Select the FIRST stylesheet only.
        var stylesheets = document.querySelectorAll('link[rel=stylesheet][href^="https://stackpath"]')
        // Update the url of the main stylesheet.
        stylesheets[stylesheets.length - 1].href = url
        // Delay update of the url of the buffer stylesheet.
        setTimeout(function() {stylesheets[0].href = url;}, 100);
    }
    """,
    Output("blank_output", "children"),
    Input("theme-dropdown", "value"),
)