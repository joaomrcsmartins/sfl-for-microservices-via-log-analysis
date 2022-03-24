from typing import Callable
import pika
from pika.channel import Channel

from sfldebug.messages.parse_message import parse_mq_message, flush_mq_messages


def setup_mq_channel(callback: Callable,
                     host: str = 'localhost', exchange: str = 'logstash-output',
                     routing_key: str = 'logstash-output') -> Channel:
    """Setup message queue connection for RabbitMQ. Returns a channel ready for consuming messages.
    Define the exchange name and the callback upon message receival.

    Args:
        callback (callable): function to be called when a message is received (required)
        host (str): target to host to setup connection (default 'localhost')
        exchange (str): name of the mq exchange to setup connection (default 'logstash-output')
        routing_key (str): name of the routing key for the mq exchange (default 'logstash-output')

    Returns:
        Channel: mq channel ready to start consuming
    """
    # Open connection in the host
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
    channel = connection.channel()

    # Define the exchange, and the appropriate params
    # By default logstash creates durable exchanges
    channel.exchange_declare(
        exchange=exchange, exchange_type='direct', durable=True)

    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    # Bind the queue to receive logs from logstash with the appropriate routing key
    channel.queue_bind(exchange=exchange, queue=queue_name,
                       routing_key=routing_key)

    # Define the action upon receiving a message
    channel.basic_consume(
        queue=queue_name, on_message_callback=callback, auto_ack=True)

    return channel


def receive_mq_messages(channel: Channel):
    """Start consuming messages from the channel, keeping it open until there is an interruption.

    Args:
        channel (pika.channel.Channel): channel to start consuming messages from (required)
    """
    try:
        print('Waiting for logs. To exit press CTRL+C')
        channel.start_consuming()
    except KeyboardInterrupt:
        flush_mq_messages()
    except OSError:
        # TODO handle interruption
        pass


def receive_mq():
    """Default receiver, relies on MQ channel."""
    channel = setup_mq_channel(parse_mq_message)
    receive_mq_messages(channel)
