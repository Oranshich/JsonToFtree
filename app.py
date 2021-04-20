from flask import Flask
import json
from flask import request
from flask_cors import CORS

app = Flask(__name__)

cors = CORS(app)
@app.route('/', methods=['POST'])
def hello_world():
    return 'Hello World!'

@app.route('/getFtree', methods=['POST'])
# @cross_origin(origin='localhost', headers=['Content- Type','Authorization'])
def getFtreeFile():
    json_file = request.data
    multilayer_dict = json.loads(json_file)
    ftree_file = '*Modules\n'
    inter_layers = []
    num_of_layers = len(multilayer_dict['layers'])

    # Adding modules (layers)
    for layer in multilayer_dict['layers']:
        ftree_file += str(layer['id']) + ' 1 ' + str(layer['name']) + ' 1\n'

    # Adding nodes
    ftree_file += '*Nodes\n'
    for link in multilayer_dict['links']:
        if link['source_layer'] != link['target_layer']:
            inter_layers.append((link['source_layer'], link['target_layer'], link['weight']))

        add_node = str(link['source_layer']) + ':' + str(link['source_node']) + ' ' + str(link['weight']) + ' \"' + \
                   str(multilayer_dict['nodes'][link['source_node'] - 1]['name']) + '\" ' + str(link['source_node']) + '\n'
        if add_node not in ftree_file:
            ftree_file += add_node
        add_node = str(link['target_layer']) + ':' + str(link['target_node']) + ' ' + str(link['weight']) + ' \"' + \
                   str(multilayer_dict['nodes'][link['target_node'] - 1]['name']) + '\" ' + str(link['target_node']) + '\n'
        if add_node not in ftree_file:
            ftree_file += add_node

    ftree_file += '*Links undirected\n'
    inter_layers_edges = ''
    num_of_inter_layers = 0
    # Add inter layer edges
    for link in inter_layers:
        add_edge_layer = str(link[0]) + ' ' + str(link[1])
        if add_edge_layer not in inter_layers_edges:
            num_of_inter_layers += 1
            inter_layers_edges += add_edge_layer + ' ' + str(link[2]) + '\n'

    ftree_file += '*Links root 0 0 ' + str(num_of_inter_layers) + ' ' + str(num_of_layers) + '\n'
    ftree_file += inter_layers_edges

    current_layer = multilayer_dict['links'][0]['source_layer']
    edges_in_layers = {current_layer: []}
    num_of_nodes_in_layer = {current_layer: set()}
    for index, edge in enumerate(multilayer_dict['links']):
        # Iterating layers and for each layer adding the intra edges
        if edge['source_layer'] != current_layer:
            current_layer = edge['source_layer']
            if current_layer not in edges_in_layers:
                edges_in_layers[current_layer] = []
                num_of_nodes_in_layer[current_layer] = set()
        if edge['source_layer'] == edge['target_layer']:
            edges_in_layers[current_layer].append(str(edge['source_node']) + ' ' + str(edge['target_node']) + ' ' + str(edge['weight']) + '\n')
            num_of_nodes_in_layer[current_layer].add(edge['source_node'])
            num_of_nodes_in_layer[current_layer].add(edge['target_node'])
        else:
            edges_in_layers[edge['source_layer']].append(str(edge['source_node']) + ' ' + str(edge['source_node']) + ' ' + str(edge['weight']) + '\n')

            if edge['target_layer'] not in edges_in_layers:
                edges_in_layers[edge['target_layer']] = []
                num_of_nodes_in_layer[edge['target_layer']] = set()

            edges_in_layers[edge['target_layer']].append(str(edge['target_node']) + ' ' + str(edge['target_node']) + ' ' + str(edge['weight']) + '\n')
            num_of_nodes_in_layer[edge['source_layer']].add(edge['source_node'])
            num_of_nodes_in_layer[edge['target_layer']].add(edge['target_node'])

    for key, value in edges_in_layers.items():
        ftree_file += '*Links ' + str(key) + ' 0 0 ' + str(len(value)) + ' ' + str(len(num_of_nodes_in_layer[key])) + '\n'
        for edge in value:
            ftree_file += edge

    ftree_file += '*Attributes\n'
    for node in multilayer_dict['nodes']:
        ftree_file += 'Node ' + str(node['id']) + '\n'
        for key, value in node.items():
            ftree_file += str(key) + ' ' + str(value) + '\n'
    response = app.response_class(
        ftree_file,
        status=200,
        mimetype="text/plain"
    )
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

if __name__ == '__main__':
    app.run()
