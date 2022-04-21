from typing import Any, Set

from sfldebug.entity import Entity
from sfldebug.tools.object import merge_into_list
import sfldebug.tools.logger as sfl_logger

default_analysis_format = {
    'good_executed': 0,
    'good_passed': 0,
    'faulty_executed': 0,
    'faulty_passed': 0
}

# each unique execution has a unique request/correlation id
unique_executions: Set[str] = set()


def increment_execution(
    entities_analyzed: dict,
    entities: Set[Entity],
    execution_key: str
) -> None:
    """Increment the number of 'execution_key' in 'entities_analyzed' for each elem of 'entities'.
    If the element is not in 'entities_analyzed', it is created and added with the increment.
    Modifies the dict in 'entities_analyzed'.
    It also updates the references and children names of the analyzed entities.

    Args:
        entities_analyzed (dict): dict to be modified with each entity analytics
        entities (Set[Entity]): set of entities to be analyzed
        execution_key (str): key to increment in
    """
    for entity in entities:
        key = '{}'.format(entity.__hash__())

        entity_requests = entity.references.keys()
        unique_executions.update(entity_requests)

        times_executed = len(entity_requests)
        if key in entities_analyzed:
            stored_entity = entities_analyzed[key]
            stored_entity[execution_key] += times_executed

            analyzed_entity_refs = stored_entity['properties']['references']
            entity_refs = entity.references
            # references of the same entity that are related to different requests
            missing_references = {k: entity_refs.get(
                k) for k in entity_refs.keys() - analyzed_entity_refs.keys()}
            # references of the same entity that are related to the same request
            merged_references = {k: merge_into_list(entity_refs.get(k), analyzed_entity_refs.get(
                k)) for k in entity_refs.keys() & analyzed_entity_refs.keys()}
            # add missing references to the stored entity
            analyzed_entity_refs.update(missing_references)
            analyzed_entity_refs.update(merged_references)
            # add missing children names to the stored entity
            analyzed_entity_children = stored_entity['properties']['children_names']
            analyzed_entity_children.update(entity.children_names)
        else:
            # if not analyzed before, create a new entry with the first references
            new_entity_analysis: dict[str, Any] = default_analysis_format.copy()
            new_entity_analysis[execution_key] += times_executed
            new_entity_analysis['properties'] = entity.get_properties()
            # and add it to the analyzed entities set
            entities_analyzed[key] = new_entity_analysis


def analyze_entities(
    good_entities: Set[Entity],
    faulty_entities: Set[Entity]
) -> dict[str, dict[str, Any]]:
    """Analyzes executions of entities. Returns a dict with analytics for each entity.
    Each element contains the number of times each entity is executed or pass in a good or faulty
    execution.

    Args:
        good_entities (Set[Entity]): entities present in a good execution
        faulty_entities (Set[Entity]): entities present in a faulty execution

    Returns:
        dict: contains for each entity the execution analytics in good and faulty settings
    """
    if len(good_entities) == 0 and len(faulty_entities) == 0:
        raise RuntimeError(
            'Good and faulty entities are empty, aborting execution.')

    entities_analyzed: dict[str, dict[str, Any]] = {}

    increment_execution(entities_analyzed, faulty_entities,
                        'faulty_executed')
    sfl_logger.logger.info('Analyzed execution of faulty entities.')

    increment_execution(entities_analyzed, good_entities, 'good_executed')
    sfl_logger.logger.info('Analyzed execution of good entities.')

    n_unique_executions = len(unique_executions)
    for entity in entities_analyzed.values():
        entity['good_passed'] = n_unique_executions - \
            entity['good_executed']
        entity['faulty_passed'] = n_unique_executions - \
            entity['faulty_executed']
    sfl_logger.logger.info(
        'Finished analyzing all entities. Number of unique executions: %d.', n_unique_executions)
    return entities_analyzed
