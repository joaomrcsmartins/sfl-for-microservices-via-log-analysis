import json
from typing import Set
from pika.channel import Channel
from pika.spec import BasicProperties, Basic

from sfldebug.entity import build_entity, parse_unique_entities, Entity
from sfldebug.tools.writer import write_results_to_file

entities = set()


def parse_mq_message(
    channel: Channel,
    method: Basic.Deliver,
    properties: BasicProperties,
    body
) -> None:
    """Callback to parse messages coming from MQ channel.

    Args:
        channel (pika.channel.Channel): message queue channel (ignored)
        method (pika.spec.Basic.Deliver): AMQP specification (ignored)
        properties (pika.spec.BasicProperties): AMQP specification (ignored)
        body (any): contents of the message
    """
    del channel, method, properties  # ignore unused arguments
    json_body = json.loads(body)
    log_entities = build_entity(json_body)
    entities.update(log_entities)


def flush_mq_messages(
    file_id: str = 'default',
    exec_id: str = 'default',
    write_to_file: bool = True
) -> Set[Entity]:
    """Once the connection is finished, parse collected entities and write to file

    Args:
        file_id (str): id of entities to record in a unique file
        exec_id (str): id of the execution to sort results
        write_to_file (bool, optional): if True, writes the parsed contents to a file. Defaults to
        True.

    Returns:
        Set[Entity]: set of parsed entities from the messages received
    """
    parsed_entities = parse_unique_entities(entities)

    if write_to_file:
        json_entities = {"entities": []}
        for entity in parsed_entities:
            json_entities['entities'].append(entity.__dict__)

        filename = 'entities-records-' + file_id
        write_results_to_file(json_entities, filename, exec_id)
    return parsed_entities
