import spacy
import re

class EntityExtractor:
    def __init__(self):
        # Load spaCy model
        self.nlp = spacy.load("en_core_web_sm")
    
    def extract_entities(self, text):
        """
        Extract named entities from text using spaCy.
        Returns a list of entities with their labels and positions.
        """
        doc = self.nlp(text)
        entities = []
        entity_map = {}  # Map to track unique entities
        
        for ent in doc.ents:
            # Clean up the entity text
            cleaned_text = self._clean_entity_text(ent.text)
            
            entity_info = {
                'text': cleaned_text,
                'label': ent.label_,
                'start': ent.start_char,
                'end': ent.end_char
            }
            entities.append(entity_info)
            
            # Track unique entities for relationship extraction
            if cleaned_text not in entity_map:
                entity_map[cleaned_text] = {
                    'text': cleaned_text,
                    'label': ent.label_
                }
        
        # Merge overlapping or related person entities
        unique_entities = self._merge_person_entities(list(entity_map.values()), entities)
        
        return {
            'mentions': entities,
            'unique_entities': unique_entities
        }
    
    def _clean_entity_text(self, text):
        """
        Clean entity text by fixing malformed quotes and other issues.
        """
        # Fix mismatched quotes (like Casey" Stengel)
        text = re.sub(r'(\w+)"(\s+\w+)', r'\1 \2', text)
        
        # Remove stray quotes at the beginning
        text = re.sub(r'^"(\w+)', r'\1', text)
        
        # Clean up extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def _merge_person_entities(self, unique_entities, all_entities):
        """
        Merge person entities that are likely referring to the same person.
        For example, merge "Charles Dillon", "Casey Stengel", and "Stengel" into one.
        """
        person_entities = [e for e in unique_entities if e['label'] == 'PERSON']
        other_entities = [e for e in unique_entities if e['label'] != 'PERSON']
        
        if len(person_entities) <= 1:
            return unique_entities
        
        # Group entities by proximity in text
        merged_persons = []
        used_indices = set()
        
        for i, person1 in enumerate(person_entities):
            if i in used_indices:
                continue
            
            # Find the full occurrence of this person in the text
            person1_mentions = [e for e in all_entities if e['text'] == person1['text']]
            
            candidates = [person1]
            
            for j, person2 in enumerate(person_entities):
                if i == j or j in used_indices:
                    continue
                
                # Check if person2 is a substring or superset of person1
                # or if they appear close together (likely the same person)
                if self._are_same_person(person1['text'], person2['text']):
                    candidates.append(person2)
                    used_indices.add(j)
            
            # Pick the longest/most complete name from candidates
            best_candidate = max(candidates, key=lambda x: len(x['text']))
            merged_persons.append(best_candidate)
            used_indices.add(i)
        
        return merged_persons + other_entities
    
    def _are_same_person(self, name1, name2):
        """
        Check if two person names likely refer to the same person.
        """
        # Normalize names
        name1_lower = name1.lower()
        name2_lower = name2.lower()
        
        # One is a substring of the other
        if name1_lower in name2_lower or name2_lower in name1_lower:
            return True
        
        # Share a last name (simple heuristic)
        name1_parts = name1.split()
        name2_parts = name2.split()
        
        if len(name1_parts) > 0 and len(name2_parts) > 0:
            # Check if last names match
            if name1_parts[-1].lower() == name2_parts[-1].lower():
                # If they share a last name and have length > 1, likely same person
                if len(name1_parts) > 1 or len(name2_parts) > 1:
                    return True
        
        return False