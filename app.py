from flask import Flask, request, jsonify , render_template, url_for, send_file, abort , send_from_directory
import json
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os

app = Flask(__name__)

# Load at startup
model = SentenceTransformer('all-MiniLM-L6-v2')
faiss_index = faiss.read_index('sfx_index.faiss')
with open('sfx_ids.json', 'r') as f:
    sound_ids = json.load(f)
with open('sfx_list_enhanced.json', 'r' , encoding='latin-1') as f:
    sfx_list = json.load(f)
sfx_dict = {s['id']: s for s in sfx_list}

@app.route("/" , methods=["GET"])
def index():
    return render_template('index.html' , index_length = len(sfx_list))



@app.route('/search-sfx', methods=['GET'])
def search_sfx():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({'error': 'Query is required'}), 400

    # Embed and search
    query_vec = model.encode([query])
    query_vec = np.array(query_vec, dtype='float32')
    faiss.normalize_L2(query_vec)

    k = 50
    similarities, indices = faiss_index.search(query_vec, k)

    results = []
    for i, idx in enumerate(indices[0]):
        if idx >= len(sound_ids):
            continue
        sound_id = sound_ids[idx]
        sound = sfx_dict.get(sound_id)
        if sound:
            if float(similarities[0][i]) > 0.4:
                results.append({
                    'id': sound['id'],
                    'title': sound['title'],
                    'description': sound['description'],
                    'tags': sound['tags'],
                    'category': sound['category'],
                    'similarity': float(similarities[0][i]),
                    'path': str(sound['path']),
                    'duration': sound['duration'],
                })
    return render_template('search_results.html', results=results , result_count = len(results) , query=query)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)