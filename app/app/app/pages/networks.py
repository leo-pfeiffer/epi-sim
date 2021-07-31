import dash_html_components as html
import dash_core_components as dcc
from ..static_elements import brand, footer, read_markdown
from ..configuration import ASSETS_DIR
import os

file = os.path.join(ASSETS_DIR, 'markdown', 'networks.md')
markdown = read_markdown(file)

text = html.Div(
    html.Div(dcc.Markdown(markdown), id='text-content'),
    id='text-container'
)

networks_page = [
    brand, footer, text
]
