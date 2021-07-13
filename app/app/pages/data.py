import dash_html_components as html

from ..static_elements import brand, footer

some_text = html.Div(
    html.Div(html.P('This is the data page'), id='text-content'),
    id='text-container'
)

data_page = [
    brand, footer, some_text
]