import requests
import time
from typing import List, Dict, Optional, Tuple

class WikidataClient:
    def __init__(self):
        self.api_url = "https://www.wikidata.org/w/api.php"
        self.sparql_url = "https://query.wikidata.org/sparql"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'EntityRelationshipExplorer/1.0'
        })
    
    def search_entity(self, entity_text: str) -> Optional[Dict]:
        """
        Search for an entity on Wikidata and return the best match with its QID and label.
        
        Args:
            entity_text: The text of the entity to search for
            
        Returns:
            Dictionary with 'qid' and 'label' if found, None otherwise
        """
        params = {
            'action': 'wbsearchentities',
            'format': 'json',
            'language': 'en',
            'type': 'item',
            'search': entity_text,
            'limit': 1
        }
        
        try:
            response = self.session.get(self.api_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('search') and len(data['search']) > 0:
                result = data['search'][0]
                return {
                    'qid': result['id'],
                    'label': result.get('label', entity_text),
                    'description': result.get('description', '')
                }
            
            return None
            
        except Exception as e:
            print(f"Error searching for entity '{entity_text}': {e}")
            return None
    
    def get_entity_label(self, qid: str) -> Optional[str]:
        """
        Get the label for a specific Wikidata entity QID.
        
        Args:
            qid: Wikidata QID (e.g., 'Q194057')
            
        Returns:
            The label string if found, None otherwise
        """
        params = {
            'action': 'wbgetentities',
            'format': 'json',
            'ids': qid,
            'props': 'labels',
            'languages': 'en'
        }
        
        try:
            response = self.session.get(self.api_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'entities' in data and qid in data['entities']:
                entity = data['entities'][qid]
                if 'labels' in entity and 'en' in entity['labels']:
                    return entity['labels']['en']['value']
            
            return None
            
        except Exception as e:
            print(f"Error getting label for {qid}: {e}")
            return None
    
    def _get_property_label(self, pid: str) -> Optional[str]:
        """
        Get the label for a specific Wikidata property PID.
        
        Args:
            pid: Wikidata PID (e.g., 'P27')
            
        Returns:
            The label string if found, None otherwise
        """
        params = {
            'action': 'wbgetentities',
            'format': 'json',
            'ids': pid,
            'props': 'labels',
            'languages': 'en'
        }
        
        try:
            response = self.session.get(self.api_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'entities' in data and pid in data['entities']:
                entity = data['entities'][pid]
                if 'labels' in entity and 'en' in entity['labels']:
                    return entity['labels']['en']['value']
            
            return None
            
        except Exception as e:
            print(f"Error getting label for property {pid}: {e}")
            return None
    
    def find_relationships(self, subject_qid: str, object_qid: str) -> List[Dict]:
        """
        Find all relationship properties between two Wikidata entities using SPARQL.
        
        Args:
            subject_qid: QID of the subject entity
            object_qid: QID of the object entity
            
        Returns:
            List of dictionaries containing relationship info (property ID and label)
        """
        # SPARQL query to find all properties connecting two entities
        query = f"""
        SELECT ?property ?propertyLabel ?prop WHERE {{
          wd:{subject_qid} ?property wd:{object_qid} .
          ?prop wikibase:directClaim ?property .
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }}
        """
        
        try:
            response = self.session.get(
                self.sparql_url,
                params={'query': query, 'format': 'json'},
                timeout=15
            )
            response.raise_for_status()
            data = response.json()
            
            relationships = []
            if 'results' in data and 'bindings' in data['results']:
                for binding in data['results']['bindings']:
                    # Get the property URI and extract PID
                    if 'prop' in binding:
                        prop_uri = binding['prop']['value']
                        property_id = prop_uri.split('/')[-1]  # Extract PID like P27
                    else:
                        property_uri = binding['property']['value']
                        property_id = property_uri.split('/')[-1]
                    
                    # Get the label - if SERVICE returned it, use it; otherwise fetch separately
                    property_label = binding.get('propertyLabel', {}).get('value', None)
                    if not property_label or property_label.startswith('http'):
                        # Label not available or is a URI, fetch it separately
                        property_label = self._get_property_label(property_id)
                        if not property_label:
                            property_label = property_id
                    
                    relationships.append({
                        'property_id': property_id,
                        'label': property_label
                    })
            
            return relationships
            
        except Exception as e:
            print(f"Error finding relationships between {subject_qid} and {object_qid}: {e}")
            return []
    
    def get_shortest_relationship(self, subject_qid: str, object_qid: str) -> Optional[Dict]:
        """
        Find the relationship with the shortest label between two entities.
        
        Args:
            subject_qid: QID of the subject entity
            object_qid: QID of the object entity
            
        Returns:
            Dictionary with the shortest relationship info, or None if no relationship found
        """
        relationships = self.find_relationships(subject_qid, object_qid)
        
        if not relationships:
            return None
        
        # Find the relationship with the shortest label
        shortest = min(relationships, key=lambda r: len(r['label']))
        return shortest
    
    def enrich_entity(self, entity_text: str) -> Dict:
        """
        Search for an entity and return enriched information including QID and label.
        
        Args:
            entity_text: The original entity text from NLP extraction
            
        Returns:
            Dictionary with original text, QID, and Wikidata label
        """
        result = {
            'original_text': entity_text,
            'qid': None,
            'wikidata_label': None,
            'description': None
        }
        
        entity_info = self.search_entity(entity_text)
        if entity_info:
            result['qid'] = entity_info['qid']
            result['wikidata_label'] = entity_info['label']
            result['description'] = entity_info['description']
        
        return result
    
    def enrich_relationship(self, subject_text: str, object_text: str, 
                           subject_qid: str, object_qid: str) -> Dict:
        """
        Find and enrich a relationship between two entities.
        
        Args:
            subject_text: Original text of subject entity
            object_text: Original text of object entity
            subject_qid: Wikidata QID of subject
            object_qid: Wikidata QID of object
            
        Returns:
            Dictionary with relationship information
        """
        result = {
            'subject': subject_text,
            'object': object_text,
            'subject_qid': subject_qid,
            'object_qid': object_qid,
            'wikidata_property': None,
            'wikidata_label': None
        }
        
        if subject_qid and object_qid:
            relationship = self.get_shortest_relationship(subject_qid, object_qid)
            if relationship:
                result['wikidata_property'] = relationship['property_id']
                result['wikidata_label'] = relationship['label']
        
        return result


def batch_enrich_entities(client: WikidataClient, entities: List[str], 
                          delay: float = 0.5) -> List[Dict]:
    """
    Enrich multiple entities with Wikidata information.
    
    Args:
        client: WikidataClient instance
        entities: List of entity text strings
        delay: Delay between requests to avoid rate limiting
        
    Returns:
        List of enriched entity dictionaries
    """
    enriched = []
    for entity_text in entities:
        enriched_entity = client.enrich_entity(entity_text)
        enriched.append(enriched_entity)
        time.sleep(delay)  # Rate limiting
    
    return enriched


def batch_enrich_relationships(client: WikidataClient, 
                               relationships: List[Tuple[str, str]], 
                               entity_qid_map: Dict[str, str],
                               delay: float = 0.5) -> List[Dict]:
    """
    Enrich multiple relationships with Wikidata information.
    
    Args:
        client: WikidataClient instance
        relationships: List of (subject, object) tuples
        entity_qid_map: Mapping from entity text to QID
        delay: Delay between requests to avoid rate limiting
        
    Returns:
        List of enriched relationship dictionaries
    """
    enriched = []
    for subject, obj in relationships:
        subject_qid = entity_qid_map.get(subject)
        object_qid = entity_qid_map.get(obj)
        
        enriched_rel = client.enrich_relationship(
            subject, obj, subject_qid, object_qid
        )
        enriched.append(enriched_rel)
        time.sleep(delay)  # Rate limiting
    
    return enriched