import dash_html_components as html
import dash_bootstrap_components as dbc


GITHUB = html.A(
    html.I(className="fab fa-github"),
    href="https://github.com/leo-pfeiffer/msc-thesis"
)

brand_wide = html.Div(
    [
        html.H2("EpiSim", className="display-4", id="app-name-wide"),
        html.Hr(),
        html.P(
            "Epidemic simulations", className="lead"
        ),
        dbc.Nav(
            [
                dbc.NavLink("Page 1", href="/page-1", active="exact"),
                dbc.NavLink("Page 2", href="/page-2", active="exact"),
                dbc.NavLink(GITHUB),
            ],
            vertical=True,
            pills=True,
        )
    ],
    id="brand-wide",
)

brand_narrow = dbc.Container(
    [
        dbc.Nav(
            [
                dbc.NavLink("EpiSim", href="/", active="exact"),
                dbc.NavLink("Page 1", href="/page-1", active="exact"),
                dbc.NavLink("Page 2", href="/page-2", active="exact"),
                dbc.NavLink(GITHUB),
            ],
            vertical=False,
            pills=True,
        ),
    ],
    id="brand-narrow"
)