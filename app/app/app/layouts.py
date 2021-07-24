from dash_bootstrap_templates import load_figure_template

px_template = "lux"
load_figure_template(px_template)

fig_layout = dict(
    margin=dict(l=10, r=10, t=10, b=0),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.15,
        xanchor="center",
        x=0.5
    ),
    # hovermode="x unified",
    autosize=True
)

main_graph_props = dict(
    x="time",
    y="value",
    color="compartment",
    hover_name="compartment",
    category_orders={"compartment": ['S', 'E', 'I', 'V', 'R']}
)
