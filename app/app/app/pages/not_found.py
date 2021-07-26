import dash_html_components as html
from ..static_elements import brand, footer

not_found_content = html.Div(
    [
        html.H1('404', id="h1-404"),
        html.H3("Either this page got eaten by the dog or it doesn't exist...", id='h3-404')],
    id='text-container',
    style={
        'text-align': 'center',
        'background-image': 'url("assets/img/dog.jpeg")',  # source: https://pixabay.com/photos/820014/
        'background-size': '100%',
        'background-repeat': 'no-repeat',
    })

not_found_page = [
    brand,
    footer,
    not_found_content
]
