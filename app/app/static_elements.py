import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc

GITHUB = html.A(
    html.I(className="fab fa-github"),
    href="https://github.com/leo-pfeiffer/msc-thesis"
)

theme_dropdown = html.Div([
    html.Label('Theme'),
    dcc.Dropdown(
        id='theme-dropdown',
        options=[{"label": m, "value": v} for m, v in [
            ('solar', dbc.themes.SOLAR),
            ('flatly', dbc.themes.FLATLY),
            ('lux', dbc.themes.LUX),
            ('cyborg', dbc.themes.CYBORG),
            ('slate', dbc.themes.SLATE),
        ]],
        value=dbc.themes.LUX,
        clearable=False),
], id='themes')

brand = html.Div(
    [
        dbc.Nav(
            [
                dbc.NavLink([html.Img(src='assets/logo.png', id='logo'), html.Span("EpiSim")], href="/", active="exact"),
                dbc.NavLink("Models", href="/model", active="exact"),
                dbc.NavLink("Data", href="/data", active="exact"),
                dbc.NavLink("About", href="/about", active="exact"),
                dbc.NavLink(GITHUB),
            ],
            vertical=False,
            pills=True,
        ),
        theme_dropdown
    ],
    id="brand"
)

footer = html.Div(
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
                    ], href=GITHUB.href, style={'color': 'black'})],
                    className='footer-content'
                ),
            ]
        )
    ], id='footer'
)