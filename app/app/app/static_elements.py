import os
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc


def read_markdown(file):
    with open(file, 'r') as fi:
        md = fi.read()
    return md


GITHUB = html.A(
    html.I(className="fab fa-github"),
    href="https://github.com/leo-pfeiffer/epi-sim"
)

brand = html.Div(
    [
        dbc.Nav(
            [
                dbc.NavLink([
                    html.Img(src='assets/img/logo.png', id='logo'),
                    html.Span("EpiSim")
                ], href="/", active="exact"),
                dbc.NavLink("Validation", href="/validation", active="exact"),
                dbc.NavLink("Models", href="/model", active="exact"),
                dbc.NavLink("Data", href="/data", active="exact"),
                dbc.NavLink("About", href="/about", active="exact"),
                dbc.NavLink(GITHUB),
                dbc.Button("Help", id="help-button", n_clicks=0),
            ],
            vertical=False,
            pills=True,
        ),
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
                        html.Strong(
                            "A Web Application for Compartmental Network "
                            "Models Illustrated Using COVID-19"),
                        "."
                    ]),
                    html.Div([
                        html.A(
                            "Leopold Pfeiffer", href="https://leopold.page"
                        ), " | ",
                        html.A(
                            "University of St Andrews",
                            href="https://www.st-andrews.ac.uk"
                        ), " | ",
                        html.A(
                            "School of Computer Science",
                            href="https://www.st-andrews.ac.uk/computer-science"
                        )
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

toast = html.Div(
    [
        dbc.Toast(
            "Click the help button in the top right corner to find out more 😊",
            id="help-toast",
            header="Need any help?",
            is_open=True,
            dismissable=True,
            duration=10000,
            icon="info",
        ),
    ]
)


# Modal ====
path = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(path, 'pages', 'markdown', 'help.md'), 'r') as f:
    markdown = f.read()

modal = html.Div(
    [
        dbc.Modal(
            [
                dbc.ModalHeader("Help"),
                dbc.ModalBody([html.Div(dcc.Markdown(markdown))]),
                dbc.ModalFooter(
                    dbc.Button(
                        "Close", id="close", className="ml-auto", n_clicks=0
                    )
                ),
            ],
            id="help-modal",
            size='xl',
            is_open=False,
            scrollable=True
        ),
    ]
)
