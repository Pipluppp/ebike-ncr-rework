from flask import Flask, request, jsonify, render_template
import osmnx as ox
import json

app = Flask(__name__)


with app.app_context():
    """Loads the Network graph before receiving requests"""
    # Load graph and stuff before running the flask app
    G = ox.io.load_graphml(filepath="data/metro_drive.graphml")
    weight = "length"

    # Load GeoDataFrame for prohibited roads
    nodes, edges = ox.graph_to_gdfs(G, edges = True)

@app.route('/')
def index():
    return render_template('voyager.html')

@app.route('/process_coords', methods=['POST'])
def process_coords():
    """Handles both source and destination coordinates and returns a path between them"""
    data = request.json
    sourceLat = data.get('sourceLat')
    sourceLng = data.get('sourceLng')
    targetLat = data.get('targetLat')
    targetLng = data.get('targetLng')

    # Get nearest nodes from the source and target
    source = ox.nearest_nodes(G, sourceLng, sourceLat)
    target = ox.nearest_nodes(G, targetLng, targetLat)

    # Run Dijkstra algorithm
    route = ox.shortest_path(G, source, target, weight=weight)
    route_gdf = ox.routing.route_to_gdf(G, route, weight=weight)
    route_geojson = json.loads(route_gdf.to_json())

    # Process the coordinates as needed
    response = {
        'message': 'Path calculated',
        'path': route,
        'route': route_geojson 
    }
    return jsonify(response)    

if __name__ == '__main__':
    app.run()