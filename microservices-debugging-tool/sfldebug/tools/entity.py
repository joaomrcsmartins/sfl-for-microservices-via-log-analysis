from enum import Enum

def build_entity(json_body: any):
    # TODO process log data into an entity reference
    pass

def parse_entities(entities):
    # TODO aggregate references to the same entities and return the resulting collection
    pass

class EntityType(Enum):
    SERVICE = 1
    CLASS = 2
    METHOD = 3
    LINE = 4
    
class Entity:
    def __init__(self, *attr) -> None:
        self.parent = None
        # TODO process arguments into class attributes
    

