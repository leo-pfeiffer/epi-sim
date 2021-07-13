fig_layout = dict(
    margin=dict(l=10, r=10, t=20, b=10),
    paper_bgcolor="white",  # paper_bgcolor="#22444a",
    font_color="black",  # font_color="#839396",
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.25,
        xanchor="center",
        x=0.5
    ),
    hovermode="x unified",
    # todo for some reason, setting transition_duration prevents loading of fig
    # transition_duration=500,
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
