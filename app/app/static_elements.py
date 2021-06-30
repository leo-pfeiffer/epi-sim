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
                dbc.NavLink("Models", href="/model", active="exact"),
                dbc.NavLink("Data", href="/data", active="exact"),
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

footer = dbc.Container(
    [
        html.Footer(
            [
                html.Div([
                    html.Hr(),
                    html.Div([
                        "Created as part of my MSc dissertation ",
                        html.Strong("A Compartmental Network Model for COVID-19"),
                        "."
                    ]),
                    html.Div([
                        html.A("Leopold Pfeiffer", href="https://leopold.page"), " | ",
                        html.A("University of St Andrews", href="https://www.st-andrews.ac.uk"), " | ",
                        html.A("School of Computer Science", href="https://www.st-andrews.ac.uk/computer-science/")
                    ]),
                    html.Hr(),
                    html.A([
                        "View on Github  ", GITHUB
                    ], href=GITHUB.href, style={'color': 'white'})],
                    className='footer-content'
                ),
            ]
        )
    ]
)