import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import plotly.express as px
from plotly.graph_objects import Figure
import os

from ..static_elements import brand, footer, read_markdown
from ..data_processing import ModelledData, EmpiricalData
from ..configuration import ASSETS_DIR


# instantiate the validation data
modelled = ModelledData()
empirical = EmpiricalData(vac_state='CT', vac_start='2021-01-01')


def make_validation_graph(name, y, title):
    model_result = modelled.get_result(name)

    # SEIVR and SEIVR_Q don't have new_case graph
    if model_result['model'] in ['SEIVR', 'SEIVR_Q'] and y == 'new_cases':
        return {}

    if model_result['model'] in ['SEIVR', 'SEIVR_Q']:
        xaxis_title = "Days since 2021-01-01"
        fig1 = px.line(empirical.vac_state, x='date', y=y)
        fig1.update_traces(
            line=dict(color="magenta", width=3),
            showlegend=True,
            name="Connecticut"
        )

    else:
        fig1 = px.line(empirical.states, x='date', y=y, color='state')
        fig1.update_traces(opacity=0.2, showlegend=True)
        xaxis_title = "Days since start of epidemic"

    model_df = model_result['data']
    fig2 = px.line(model_df, x='time', y=y)
    fig2.update_traces(
        line=dict(color="blue", width=3),
        showlegend=True,
        name='Model'
    )

    fig = Figure(data=fig2.data + fig1.data)
    fig.update_layout(
        title=title,
        xaxis_title=xaxis_title,
        yaxis_title="Fraction of population",
    )

    return fig


def make_new_case_plot(name):
    fig = make_validation_graph(name, 'new_cases', 'New cases per day')
    return fig


def make_total_case_plot(name):
    fig = make_validation_graph(name, 'tot_cases', 'Total cumulative cases')
    return fig


def make_description_card(filename):
    file = os.path.join(ASSETS_DIR, 'markdown', filename)
    return read_markdown(file)


total_cases = dbc.Card([
    dbc.CardBody(
        dcc.Graph(id='total-cases-graph', responsive=True)
    )
], id='total-cases')

new_cases = dbc.Card([
    dbc.CardBody(
        dcc.Graph(id='new-cases-graph', responsive=True)
    )
], id='new-cases')

description = dbc.Card([
    dbc.CardBody(
        dcc.Markdown(make_description_card('validation.md')),
        style={'overflowY': 'auto', 'height': '100%'}
    )
], id='validation-description')

validation_control = dbc.Card([
    html.Div([
        html.Label('Validation Setting'),
        dcc.RadioItems(
            id='validation-dropdown',
            options=[
                {"label": v['title'], "value": v['name']}
                for v in modelled.VALIDATION_FILES
            ],
            value=modelled.VALIDATION_FILES[0]['name']
        ),
    ])
], body=True, id='validation-controls')

text = html.Div(
    html.Div([

    ], id='text-content'),
    id='text-container'
)

validation_page = [
    brand,
    footer,
    validation_control,
    total_cases,
    new_cases,
    description
]
