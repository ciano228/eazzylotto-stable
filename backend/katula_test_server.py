from flask import Flask, send_from_directory, jsonify
import json
import os

app = Flask(__name__, static_folder='frontend')

# Load the validated structure once at startup
with open('backend/katula_validated_structure.json', 'r', encoding='utf-8') as f:
    KATULA_DATA = json.load(f)

@app.route('/')
def index():
    return send_from_directory('frontend', 'katula-modular.html')

@app.route('/modules/katula/<path:filename>')
def serve_module(filename):
    return send_from_directory('frontend/modules/katula', filename)

@app.route('/api/katula/<universe>')
def get_universe(universe):
    if universe in KATULA_DATA['universes']:
        return jsonify(KATULA_DATA['universes'][universe])
    return jsonify({'error': 'Universe not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)