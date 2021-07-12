import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import plotly.express as px
from app.layouts import fig_layout, fig_traces, px_line_props, table_layout  # noqa


def make_dropdown(label, dropdown_options, clearable=False, div_id=''):
    return html.Div([
        html.Label(label),
        dcc.Dropdown(**dropdown_options, clearable=clearable),
    ], id=div_id)


def make_slider(label, slider_options):
    return html.Div([
        html.Label([label, ': ', html.Span(id={'type': 'label', 'index': slider_options['id']['index']})]),
        dcc.Slider(**slider_options)
    ])


def create_heatmap_figure():
    fig = go.Figure(data=go.Heatmap(
        z=[[1, 20, 30],
           [20, 1, 60],
           [30, 60, 1]]))

    fig.update_layout(**fig_layout)
    return fig


def create_waterfall_figure():
    df = px.data.iris()
    fig = px.scatter(df, x="sepal_width", y="sepal_length")
    fig.update_layout(**fig_layout)
    return fig
