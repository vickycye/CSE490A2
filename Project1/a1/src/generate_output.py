import argparse
import json
from entity_extractor import EntityExtractor
from relationship_extractor import RelationshipExtractor
from wikidata_client import WikidataClient

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Extract entities and relationships from text')
    parser.add_argument('--input', required=True, help='Input text file')
    parser.add_argument('--output', required=True, help='Output file')
    args = parser.parse_args()
    
    # Read input
    with open(args.input, 'r') as f:
        text = f.read().strip()
    
    # Initialize extractors
    entity_extractor = EntityExtractor()
    relationship_extractor = RelationshipExtractor()
    wikidata_client = WikidataClient()
    
    # Extract entities and relationships
    entities = entity_extractor.extract_entities(text)
    relationships = relationship_extractor.extract_relationships(text, entities)
    
    # Enrich entities with Wikidata
    entity_qid_map = {}
    entity_label_map = {}
    
    print(f"Extracting {len(entities['unique_entities'])} entities...")
    for entity in entities['unique_entities']:
        entity_text = entity['text']
        entity_info = wikidata_client.search_entity(entity_text)
        if entity_info:
            entity_qid_map[entity_text] = entity_info['qid']
            entity_label_map[entity_text] = entity_info['label']
            print(f"  - {entity_text} -> {entity_info['qid']}")
        else:
            print(f"  - {entity_text} -> No QID found")
    
    # Write output in the specified format
    output_lines = []
    processed_entities = set()  # Track which entities are used in relationships
    
    print(f"\nEnriching {len(relationships)} relationships...")
    for rel in relationships:
        subject = rel['subject']
        obj = rel['object']
        
        subject_qid = entity_qid_map.get(subject)
        object_qid = entity_qid_map.get(obj)
        
        if subject_qid and object_qid:
            # Find relationship from Wikidata
            relationship_info = wikidata_client.get_shortest_relationship(subject_qid, object_qid)
            
            if relationship_info:
                predicate = relationship_info['label']
                predicate_pid = relationship_info['property_id']
                
                output_dict = {
                    'subject': subject,
                    'subject_qid': subject_qid,
                    'predicate': predicate,
                    'predicate_pid': predicate_pid,
                    'object': obj,
                    'object_qid': object_qid
                }
                
                # Format as requested: single quotes for JSON
                output_line = str(output_dict).replace('"', "'")
                output_lines.append(output_line)
                processed_entities.add(subject)
                processed_entities.add(obj)
                print(f"  ✓ ({subject}, {predicate}, {obj})")
            else:
                print(f"  ✗ No relationship found between {subject} and {obj}")
        else:
            if not subject_qid:
                print(f"  ✗ Missing QID for subject: {subject}")
            if not object_qid:
                print(f"  ✗ Missing QID for object: {obj}")
    
    # Add entities that have QIDs but no relationships (Task-1 only)
    print(f"\nAdding entities without relationships...")
    for entity_text, entity_qid in entity_qid_map.items():
        if entity_text not in processed_entities:
            output_dict = {
                'subject': entity_text,
                'subject_qid': entity_qid,
                'predicate': '',
                'predicate_pid': '',
                'object': '',
                'object_qid': ''
            }
            output_line = str(output_dict).replace('"', "'")
            output_lines.append(output_line)
            print(f"  + {entity_text} ({entity_qid})")
    
    # Write output
    with open(args.output, 'w') as f:
        for line in output_lines:
            f.write(line + '\n')
    
    print(f"\nOutput written to {args.output}")
    print(f"Total lines: {len(output_lines)}")

if __name__ == '__main__':
    main()
