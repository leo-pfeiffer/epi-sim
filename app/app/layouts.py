fig_layout = dict(
    margin=dict(l=20, r=20, t=35, b=5),
    paper_bgcolor="#22444a",
    font_color="#839396",
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.25,
        xanchor="center",
        x=0.5
    ),
    hovermode="x unified",
    # todo for some reason, setting transition_duration prevents loading of fig
    # transition_duration=500
)

fig_traces = dict(
    mode="lines",
    hovertemplate=None
)

px_line_props = dict(
    x="time",
    y="value",
    color="compartment",
    facet_col="network",
    line_group="compartment",
    hover_name="compartment",
    template="plotly_white"
)

table_layout = dict(
    cell_selectable=False,
    style_cell={
        'padding': '5px',
        'textAlign': 'left',
        'backgroundColor': '#38535a',
        'color': 'white',
    },
    style_header={
        'fontWeight': 'bold'
    },
    style_as_list_view=True
)