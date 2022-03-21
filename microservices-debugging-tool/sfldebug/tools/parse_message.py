import json
import pika.channel.Channel as Channel
import pika.spec.Basic.Deliver as Deliver
import pika.spec.BasicProperties as BasicProperties
 
from tools.entity import build_entity, parse_entities

entities = None

def parse_mq_message(channel: Channel, method: Deliver, properties: BasicProperties, body):
    """Callback to parse messages coming from MQ channel.

    Args:
        channel (pika.channel.Channel): message queue channel (ignored)
        method (pika.spec.Basic.Deliver): AMQP specification (ignored)
        properties (pika.spec.BasicProperties): AMQP specification (ignored)
        body (Any): contents of the message
    """
    json_body = json.loads(body)
    entity = build_entity(json_body)
    entities.append(entity)

def flush_mq_messages():
    """Once the connection is finished, parse collected entities and write to file"""
    parsed_entities = parse_entities(entities)
    with open('entities-records.json','w') as f:
        json_entities = {"entities": parsed_entities}
        f.write(json.dumps(json_entities, indent=2, sort_keys=True))

def __init__():
    """Initialize entities"""
    entities = []