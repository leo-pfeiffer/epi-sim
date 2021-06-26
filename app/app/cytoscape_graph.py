import networkx as nx
import dash_cytoscape as cyto


def graph_elements(n=20):
    G = nx.erdos_renyi_graph(n=n, p=0.2)
    pos = nx.spring_layout(G, seed=4, scale=10000)
    cy = nx.readwrite.json_graph.cytoscape_data(G)

    max_degree = max(dict(G.degree).values())

    for n in cy['elements']['nodes']:
        node_id = int(n['data']['id'])

        # rename value to label
        n['data']['label'] = node_id
        n['data']['color'] = perc_to_color(G.degree[node_id] / max_degree)

        # add postitions
        n['position'] = {'x': pos[node_id][0], 'y': pos[node_id][1]}

    elements_ls = cy['elements']['nodes'] + cy['elements']['edges']

    return elements_ls


def perc_to_color(perc, max_hue=360, min_hue=260):
    hue = perc * (max_hue - min_hue) + min_hue
    return f'hsl({hue}, 100%, 50%)'


cyto_stylesheet = [
    {
        'selector': 'node',
        'style': {
            'background-color': 'data(color)',
            'label': '',
            'width': "60px",
            'height': "60px"
        }
    },
    {
        "selector": "edge",
        "style": {
            # 'line-color': '#808080',
            'line-color': 'white',
        }
    }
]

elements_ls = graph_elements(30)

cyto_graph = cyto.Cytoscape(
    id='cytoscape',
    elements=elements_ls,
    layout={'name': 'preset'},
    style={
        'height': '600px',
        "border": "solid #839396",
        "border-radius": "3px",
    },
    stylesheet=cyto_stylesheet
)
