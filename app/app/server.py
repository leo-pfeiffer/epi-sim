import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, MATCH, ClientsideFunction

# page utils
from .pages.index import make_main_graph, make_detail_table, \
    make_heatmap, make_waterfall, filter_df

# pages
from .pages import *

FONT_AWESOME = 'https://pro.fontawesome.com/releases/v5.10.0/css/all.css'

external_stylesheets = [
    dbc.themes.SOLAR,
    dbc.themes.SOLAR,
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
    Output('epidemic-curve-graph', 'figure'),
    Output('table-card-body', 'children'),
    Input('model-dropdown', 'value'),
    Input('network-dropdown', 'value')
)
def graph_callback(model, network):

    network = 'MN_pre'

    df = filter_df(model, network)
    fig = make_main_graph(df)
    table_df = make_detail_table(df)

    table = dbc.Table.from_dataframe(
        table_df, striped=True, bordered=True, hover=True, responsive=True,
        id='summary-data-table', className='table'
    )

    return fig, table


@app.callback(
    Output({'type': 'label', 'index': MATCH}, 'children'),
    Input({'type': 'slider', 'index': MATCH}, 'value')
)
def slider_callback(value):
    return value


@app.callback(
    Output("waterfall-graph", "figure"),
    Input("waterfall-card-tabs", "active_tab")
)
def waterfall_tabs(active_tab):
    return make_waterfall()


@app.callback(
    Output("heatmap-graph", "figure"),
    Input("heatmap-card-tabs", "active_tab")
)
def heatmap_tabs(active_tab):
    return make_heatmap()


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

app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='switchStylesheet'
    ),
    Output('blank_output', 'style'),
    Input('url', 'pathname')
)


# Update the index
@app.callback(Output('page', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    print(pathname)
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
    # You could also return a 404 "URL not found" page here
