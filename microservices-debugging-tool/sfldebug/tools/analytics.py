from typing import Set
from sfldebug.entity import Entity

default_analysis_format = {
    'good_executed': 0,
    'good_passed': 0,
    'faulty_executed': 0,
    'faulty_passed': 0
}

unique_executions: Set[str] = set()


def increment_execution(entities_analyzed: dict, entities: Set[Entity], execution_key: str):
    """Increment the number of 'execution_key' in 'entities_analyzed' for each elem of 'entities'.
    If the element is not in 'entities_analyzed', it is created and added with the increment.
    Modifies the dict in 'entities_analyzed'.

    Args:
        entities_analyzed (dict): dict to be modified with each entity analytics
        entities (Set[Entity]): set of entities to be analyzed
        execution_key (str): key to increment in
    """
    for entity in entities:
        key = "{}".format(entity.__hash__())

        unique_executions.update([ref['request_id']
                                 for ref in entity.references])
        if key in entities_analyzed:
            entities_analyzed[key][execution_key] += 1
            entities_analyzed[key]['properties']['references'] += entity.references
        else:
            new_entity_analysis = default_analysis_format.copy()
            new_entity_analysis[execution_key] += 1
            new_entity_analysis['properties'] = entity.get_properties()
            entities_analyzed[key] = new_entity_analysis


def analyze_entities(good_entities: Set[Entity], faulty_entities: Set[Entity]) -> dict:
    """Analyzes executions of entities. Returns a dict with analytics for each entity.
    Each element contains the number of times each entity is executed or pass in a good or faulty
    execution.

    Args:
        good_entities (Set[Entity]): entities present in a good execution
        faulty_entities (Set[Entity]): entities present in a faulty execution

    Returns:
        dict: contains for each entity the execution analytics in good and faulty settings
    """
    entities_analyzed: dict = {}

    increment_execution(entities_analyzed, faulty_entities,
                        'faulty_executed')
    increment_execution(entities_analyzed, good_entities, 'good_executed')

    n_unique_executions = len(unique_executions)
    for entity in entities_analyzed.values():
        entity['good_passed'] = n_unique_executions - \
            entity['good_executed']
        entity['faulty_passed'] = n_unique_executions - \
            entity['faulty_executed']

    return entities_analyzed
