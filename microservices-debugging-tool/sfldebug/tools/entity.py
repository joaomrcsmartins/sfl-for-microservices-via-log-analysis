from enum import Enum
from typing import Any, Set

class EntityType(Enum):
    SERVICE = 1
    CLASS = 2
    METHOD = 3
    
class Entity:
    def __init__(self, requestID: str, type: EntityType = EntityType.SERVICE, fileName: str = None, lineRef: int = None ):
        self.parent = None
        self.child = []
        self.type = type
        self.fileName = fileName
        self.lineRef = lineRef
        
def build_entity(log_data: Any) -> None: #Set[Entity]:
    """Generates and returns the entities present in log object.
    Each log object points to a entity, more or less specific.
    Generate a entity object of each type with equal or less specificity.
    Ex.: if the log points to a method, generate method, class, and service entities.
    If the log points to a class, generate class and service entities.

    Args:
        log_data (Any): log content formatted in an object

    Returns:
        Set[Entity]: set of entities generated from parsing the log data
    """
    print(log_data)
    

def parse_entities(entities) -> Set[Entity]:
    # TODO aggregate references to the same entities and return the resulting collection
    pass


    

