import json
from typing import Set
from pika.channel import Channel
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import BasicProperties, Basic

from sfldebug.entity import build_entity, parse_unique_entities, Entity
from sfldebug.tools.writer import write_results_to_file

entities = set()


def channel_stop(
    channel: BlockingChannel,
    method: Basic.Deliver,
    properties: BasicProperties,
    body
) -> None:
    """Callback to stop channel consuming and break I/O loop.

    Args:
        channel (BlockingChannel): message queue channel to be shutdown
        method (Basic.Deliver): AMQP specification (ignored)
        properties (BasicProperties): AMQP specification (ignored)
        body (any): AMQP specification (ignored)
    """
    del method, properties, body
    channel.stop_consuming()


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
    parse_json_entity(body)


def parse_json_entity(message: str):
    """Parse a message into json and build the entity from the structured data. Update the entities
    set.

    Args:
        message (str): The message in json line format to be parsed
    """
    message_json = json.loads(message)
    log_entities = build_entity(message_json)
    entities.update(log_entities)


def clear_entities():
    """Clear the entities set. Useful when running multiple scenarios in a row."""
    entities.clear()


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
            entity_dict = entity.__dict__
            entity_dict['ref_count'] = Entity.count_references(
                entity_dict['references'])
            json_entities['entities'].append(entity_dict)

        filename = 'entities-records-' + file_id
        write_results_to_file(json_entities, filename, exec_id)
    return parsed_entities
