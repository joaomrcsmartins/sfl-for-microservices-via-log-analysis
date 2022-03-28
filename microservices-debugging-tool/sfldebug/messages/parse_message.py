import json
from typing import Set
from pika.channel import Channel
from pika.spec import BasicProperties, Basic

from sfldebug.entity import build_entity, parse_unique_entities, Entity
from sfldebug.tools.writer import write_json_to_file
entities = set()


def parse_mq_message(channel: Channel, method: Basic.Deliver, properties: BasicProperties, body):
    """Callback to parse messages coming from MQ channel.

    Args:
        channel (pika.channel.Channel): message queue channel (ignored)
        method (pika.spec.Basic.Deliver): AMQP specification (ignored)
        properties (pika.spec.BasicProperties): AMQP specification (ignored)
        body (any): contents of the message
    """
    del channel, method, properties  # ignore unused arguments
    json_body = json.loads(body)
    print('Received message.')
    log_entities = build_entity(json_body)
    entities.update(log_entities)


def flush_mq_messages(file_id: str) -> Set[Entity]:
    """Once the connection is finished, parse collected entities and write to file

    Args:
        file_id (str): id of entities to record in a unique file
    """
    parsed_entities = parse_unique_entities(entities)

    json_entities = {"entities": []}
    for entity in parsed_entities:
        json_entities['entities'].append(entity.__dict__)

    filename = 'entities-records-' + file_id
    write_json_to_file(json_entities, filename)
    return parsed_entities
