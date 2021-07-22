import dash_html_components as html
import dash_core_components as dcc
from ..static_elements import brand, footer
import os

path = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(path, 'markdown', 'model.md'), 'r') as f:
    markdown = f.read()

text = html.Div(
    html.Div(dcc.Markdown(markdown), id='text-content'),
    id='text-container'
)
model_page = [
    brand, footer, text
]
