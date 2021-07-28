import dash_html_components as html
import dash_core_components as dcc
from ..static_elements import brand, footer, read_markdown
import os

path = os.path.dirname(os.path.abspath(__file__))
file = os.path.join(path, 'markdown', 'model.md')
markdown = read_markdown(file)

text = html.Div(
    html.Div(dcc.Markdown(markdown), id='text-content'),
    id='text-container'
)
model_page = [
    brand, footer, text
]
