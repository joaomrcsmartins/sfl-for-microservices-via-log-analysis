#import signal
import multiprocessing as mp
import logging
from typing import Callable, Set
from pika import BlockingConnection, ConnectionParameters
from pika.adapters.blocking_connection import BlockingChannel
from pika.exchange_type import ExchangeType

from sfldebug.messages.parse_message import parse_mq_message, flush_mq_messages
from sfldebug.tools.logger import config_logger, logger
from sfldebug.entity import Entity


def setup_mq_channel(
    callback: Callable,
    host: str = 'localhost',
    exchange: str = 'logstash-output',
    routing_key: str = 'logstash-output'
) -> BlockingChannel:
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
    connection = BlockingConnection(ConnectionParameters(host=host))
    channel = connection.channel()

    # Define the exchange, and the appropriate params
    # By default logstash creates durable exchanges
    channel.exchange_declare(
        exchange=exchange, exchange_type=ExchangeType.direct, durable=True)

    result = channel.queue_declare(queue='')
    queue_name = result.method.queue

    # Bind the queue to receive logs from logstash with the appropriate routing key
    channel.queue_bind(exchange=exchange, queue=queue_name,
                       routing_key=routing_key)

    # Define the action upon receiving a message
    channel.basic_consume(
        queue=queue_name, on_message_callback=callback, auto_ack=True)

    logger.debug('Channel set up for exchange "%s", type "%s", routing key "%s", and host "%s"',
                 exchange, ExchangeType.direct, routing_key, host)
    return channel


def receive_mq_messages(
    execution_id: str,
    callback: Callable,
    host: str = 'localhost',
    exchange: str = 'logstash-output',
    routing_key: str = 'logstash-output'
) -> Set[Entity]:
    """Start consuming messages from the channel, keeping it open until there is an interruption.

    Args:
        Args:
        execution_id (str): id of the current execution
        callback (callable): function to be called when a message is received (required)
        host (str): target to host to setup connection (default 'localhost')
        exchange (str): name of the mq exchange to setup connection (default 'logstash-output')
        routing_key (str): name of the routing key for the mq exchange (default 'logstash-output')
    """
    config_logger(execution_id) # necessary when using multiprocessesing

    channel = setup_mq_channel(callback, host, exchange, routing_key)
    logger.info('"%s" - Waiting for logs. Press CTRL+C to terminate', exchange)
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        # TODO improve communications interruption handling
        logger.info(
            '"%s" - Terminating connection... Flushing collected messages!', exchange)
        channel.close()
        logger.info('"%s" - Flushed collected messages', exchange)
    return flush_mq_messages(exchange, execution_id)


def receive_mq(
    good_entities_id: str,
    faulty_entities_id: str,
    execution_id: str
) -> dict:
    """Receives log data through MQ channels.
    Each channel receives the messages and sends the data to a parser.
    The channels are set up in different processes for concurrent receival of messages.
    Returns a set with the parsed data for the 'good' and 'faulty' entities.

    Args:
        good_entities_id (str): name of the exchange where the good entities' log data will
        originate from
        faulty_entities_id (str): name of the exchange where the faulty entities' log data will
        originate from
        execution_id (str): id of the current execution

    Returns:
        dict: set with the parsed data for the 'good' and 'faulty' entities
    """

    # silence mp logging when KeyboardInterrupt happens. Remember to comment when debugging
    mp.log_to_stderr(logging.NOTSET)
    with mp.Pool(2) as pool:

        logger.info('Opening channels: "%s" and "%s"',
                    good_entities_id, faulty_entities_id)

        good_entities_process = pool.apply_async(
            receive_mq_messages,
            args=(execution_id, parse_mq_message),
            kwds={'exchange': good_entities_id, 'routing_key': good_entities_id})
        faulty_entities_process = pool.apply_async(
            receive_mq_messages,
            args=(execution_id, parse_mq_message),
            kwds={'exchange': faulty_entities_id, 'routing_key': faulty_entities_id})
        good_entities: Set[Entity] = set()
        faulty_entities: Set[Entity] = set()
        try:
            good_entities_process.wait()
            faulty_entities_process.wait()
        except KeyboardInterrupt:
            # TODO improve error handling
            logger.debug("Keyboard Interruption on MQ receivers.")
            good_entities = good_entities_process.get()
            faulty_entities = faulty_entities_process.get()

        logger.info('Message receiving complete.')
        return {good_entities_id: good_entities, faulty_entities_id: faulty_entities}
