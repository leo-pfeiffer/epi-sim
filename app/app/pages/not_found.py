import dash_html_components as html

from ..static_elements import brand, footer

some_text = html.Div(
    html.P('This page does not exist'),
    id='text-content'
)

not_found_page = [
    brand, footer, some_text
]