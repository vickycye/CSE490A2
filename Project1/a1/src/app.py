from flask import Flask, render_template, request, jsonify
from entity_extractor import EntityExtractor
from relationship_extractor import RelationshipExtractor
from wikidata_client import WikidataClient, batch_enrich_entities, batch_enrich_relationships

app = Flask(__name__)

# Initialize extractors
entity_extractor = EntityExtractor()
relationship_extractor = RelationshipExtractor()
wikidata_client = WikidataClient()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_text():
    data = request.json
    text = data.get('text', '')
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    # Extract entities
    entities = entity_extractor.extract_entities(text)
    
    # Extract relationships
    relationships = relationship_extractor.extract_relationships(text, entities)
    
    return jsonify({
        'entities': entities,
        'relationships': relationships
    })

@app.route('/enrich', methods=['POST'])
def enrich_with_wikidata():
    """
    Enrich entities and relationships with Wikidata information.
    """
    data = request.json
    entities = data.get('entities', [])
    relationships = data.get('relationships', [])
    
    if not entities:
        return jsonify({'error': 'No entities provided'}), 400
    
    # Enrich entities
    enriched_entities = batch_enrich_entities(
        wikidata_client, 
        [e['text'] for e in entities]
    )
    
    # Create QID mapping for relationship enrichment
    entity_qid_map = {
        e['original_text']: e['qid'] 
        for e in enriched_entities if e['qid']
    }
    
    # Enrich relationships
    enriched_relationships = []
    if relationships:
        relationship_pairs = [
            (r['subject'], r['object']) 
            for r in relationships
        ]
        enriched_relationships = batch_enrich_relationships(
            wikidata_client,
            relationship_pairs,
            entity_qid_map
        )
    
    return jsonify({
        'enriched_entities': enriched_entities,
        'enriched_relationships': enriched_relationships
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)