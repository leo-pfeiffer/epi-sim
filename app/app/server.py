from typing import Union

import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px

from app.data_import import data  # noqa
from app.static_elements import brand, footer  # noqa
from app.layouts import fig_layout, fig_traces, px_line_props, table_layout  # noqa
from app.factory import make_dropdown, make_slider, create_waterfall_figure, create_heatmap_figure  # noqa

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
    id='p-quarantine-slider', min=0, max=1, step=0.1, value=0))

vaccine_slider = make_slider('P_VACCINE', dict(
    id='p-vaccine-slider', min=0, max=1, step=0.1, value=0))

vaccine_init_slider = make_slider('P_VACCINE_INIT', dict(
    id='p-vaccine-init-slider', min=0, max=1, step=0.1, value=0))

rrr_slider = make_slider('RRR', dict(
    id='rrr-slider', min=0, max=1, step=0.1, value=0))

ctrls = [model_dropdown, network_dropdown, quarantine_slider, vaccine_slider,
         vaccine_init_slider, rrr_slider]

controls = dbc.Card(ctrls, body=True, id='controls')

somefig = dbc.Card([
    dbc.CardBody([dcc.Graph(id='my-graph')])
], id='main')

sometab = dbc.Card([
    dash_table.DataTable(
        id='my-table',
        columns=[{"name": i, "id": i} for i in ['col1', 'col2']],
        data=[{'col1': 1, 'col2': 1}, {'col1': 2, 'col2': 2}], **table_layout)
], body=True, id='table')

waterfall = dbc.Card([
        dbc.CardBody([dcc.Graph(figure=create_waterfall_figure())])
], id='waterfall')

heatmap = dbc.Card([
        dbc.CardBody([dcc.Graph(id="heatmap-figure", figure=create_heatmap_figure())])
], id='heatmap')

app.layout = html.Div([
    dcc.Location(id="url"), brand, controls, footer, somefig, sometab, waterfall, heatmap, html.Div(id="blank_output")
], id="page")


# CALLBACKS ====
@app.callback(
    Output('my-graph', 'figure'),
    Output('my-table', 'data'),
    Output('my-table', 'columns'),
    Input('model-dropdown', 'value'),
    Input('network-dropdown', 'value'),
)
def graph_callback(model, network):

    network='MN_pre'

    filtered_df = data[model]['df'][data[model]['df'].network == network]

    fig = create_main_figure(filtered_df)
    dat, cols = create_detail_table(filtered_df)

    return fig, dat, cols


def create_main_figure(filtered_df):
    fig = px.line(filtered_df, **px_line_props)
    fig.update_traces(**fig_traces)
    fig.update_layout(**fig_layout)
    return fig


def create_detail_table(df):
    out = {}

    last_time = df[df.time == max(df.time)]

    out['total infected'] = calc_perc_infected(last_time)
    out['susceptible remaining'] = calc_susceptible_remaining(last_time)
    out['peak time'] = calc_peak_time(df)
    out['peak infected'] = calc_peak_infected(df)
    out['effective end'] = calc_effective_end(df)

    for k, v in out.items():
        out[k] = '%.4f' % v

    columns = [{"name": i, "id": i} for i in ['key', 'value']]
    records = [{'key': k, 'value': v} for k, v in out.items()]

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