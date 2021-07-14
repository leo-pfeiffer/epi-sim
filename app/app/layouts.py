fig_layout = dict(
    margin=dict(l=10, r=10, t=20, b=10),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.25,
        xanchor="center",
        x=0.5
    ),
    hovermode="x unified",
    transition_duration=500,
)

fig_traces = dict(
    mode="lines",
    hovertemplate=None
)

px_line_props = dict(
    x="time",
    y="value",
    color="compartment",
    line_group="compartment",
    hover_name="compartment",
    template="plotly_white"
)
