import spacy

class RelationshipExtractor:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
    
    def extract_relationships(self, text, entities):
        """
        Extract relationships between entities using dependency parsing.
        Returns a list of (subject, predicate, object) triplets.
        """
        doc = self.nlp(text)
        relationships = []
        
        # Create a mapping from token indices to entity text
        token_to_entity = {}
        for ent in doc.ents:
            for token in ent:
                token_to_entity[token.i] = ent.text
        
        # Look for verbs and auxiliaries that might indicate relationships
        for token in doc:
            if token.pos_ in ["VERB", "AUX"]:
                subject_entity = None
                object_entity = None
                predicate = token.lemma_
                
                # Find subject
                for child in token.children:
                    if child.dep_ in ["nsubj", "nsubjpass"]:
                        subject_entity = self._get_entity_for_token(child, token_to_entity)
                
                # Find object through prepositional phrases or direct objects
                for child in token.children:
                    if child.dep_ == "prep":
                        # Look for pobj under the preposition
                        for prep_child in child.children:
                            if prep_child.dep_ == "pobj":
                                object_entity = self._get_entity_for_token(prep_child, token_to_entity)
                                if subject_entity and object_entity:
                                    # Include preposition in predicate
                                    predicate = f"{token.lemma_} {child.text}"
                                    relationships.append({
                                        'subject': subject_entity,
                                        'predicate': predicate,
                                        'object': object_entity
                                    })
                    elif child.dep_ in ["dobj", "attr"]:
                        object_entity = self._get_entity_for_token(child, token_to_entity)
                        if subject_entity and object_entity:
                            relationships.append({
                                'subject': subject_entity,
                                'predicate': predicate,
                                'object': object_entity
                            })
                    elif child.dep_ == "pobj":
                        object_entity = self._get_entity_for_token(child, token_to_entity)
                        if subject_entity and object_entity:
                            relationships.append({
                                'subject': subject_entity,
                                'predicate': predicate,
                                'object': object_entity
                            })
        
        return relationships
    
    def _get_entity_for_token(self, token, token_to_entity):
        """
        Get the entity text for a token, following compound and proper noun chains.
        """
        # Check if token is directly mapped to an entity
        if token.i in token_to_entity:
            return token_to_entity[token.i]
        
        # Check if any child tokens are entities (for compound structures)
        for child in token.children:
            if child.i in token_to_entity:
                return token_to_entity[child.i]
        
        # Check the token's subtree for entities
        for descendant in token.subtree:
            if descendant.i in token_to_entity:
                return token_to_entity[descendant.i]
        
        return None
