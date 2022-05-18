#import signal
import multiprocessing as mp
import logging
from typing import Callable, Set
from pika import BlockingConnection, ConnectionParameters
from pika.adapters.blocking_connection import BlockingChannel

import sfldebug.tools.logger as sfl_logger
import sfldebug.messages.parse_message as pm
import sfldebug.tools.object as sfl_obj
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
    channel.exchange_declare(exchange=exchange, durable=True)

    result = channel.queue_declare(queue='', durable=True)
    queue_name = result.method.queue

    # Bind the queue to receive logs from logstash with the appropriate routing key
    channel.queue_bind(exchange=exchange, queue=queue_name,
                       routing_key=routing_key)

    channel.basic_qos(prefetch_count=1)
    # Define the action upon receiving a message
    channel.basic_consume(
        queue=queue_name, on_message_callback=callback, auto_ack=True)

    # Define the action to stop consuming when a message through 'channel-stop' is received
    channel.exchange_declare(exchange='channel-stop', durable=True)
    stop_queue = channel.queue_declare(queue='channel-stop', durable=True)
    stop_queue_name = stop_queue.method.queue
    channel.queue_bind(exchange='channel-stop',
                       routing_key='', queue=stop_queue_name)
    channel.basic_consume('channel-stop', pm.channel_stop, auto_ack=True)

    sfl_logger.logger.debug(
        'Channel set up for exchange "%s", type "direct", routing key "%s", and host "%s".',
        exchange, routing_key, host)
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
    sfl_logger.config_logger(
        execution_id)  # necessary when using multiprocessesing

    channel = setup_mq_channel(callback, host, exchange, routing_key)
    sfl_logger.logger.info(
        '"%s" - Waiting for logs. Press CTRL+C to terminate.', exchange)
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        sfl_logger.logger.debug(
            '"%s" - Terminating connection from keyboard interruption.', exchange)
    sfl_logger.logger.info(
        '"%s" - Terminating connection... Flushing collected messages!', exchange)
    channel.close()
    return pm.flush_mq_messages(exchange, execution_id)


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

    # stop mp logging on KeyboardInterrupts. Comment when debugging
    mp.log_to_stderr(logging.NOTSET)
    with mp.Pool(2) as pool:

        sfl_logger.logger.info('Opening channels: "%s" and "%s".',
                               good_entities_id, faulty_entities_id)

        good_entities_process = pool.apply_async(
            receive_mq_messages,
            args=(execution_id, pm.parse_mq_message),
            kwds={'exchange': good_entities_id, 'routing_key': good_entities_id})
        faulty_entities_process = pool.apply_async(
            receive_mq_messages,
            args=(execution_id, pm.parse_mq_message),
            kwds={'exchange': faulty_entities_id, 'routing_key': faulty_entities_id})

        good_entities: Set[Entity] = set()
        faulty_entities: Set[Entity] = set()
        try:
            good_entities_process.wait()
            faulty_entities_process.wait()
        except KeyboardInterrupt:
            sfl_logger.logger.debug('Keyboard Interruption on MQ receivers.')
        good_entities = good_entities_process.get()
        faulty_entities = faulty_entities_process.get()

        sfl_logger.logger.info('Message receiving complete.')
        return {good_entities_id: good_entities, faulty_entities_id: faulty_entities}


def receive_file(
    good_entities_file: str,
    faulty_entities_file: str,
    execution_id: str
) -> dict:
    """Receives log data through files.
    Open each file and extract the entities contained in each line.
    Each line must be in a stringified json format.
    Then for each file the entities set is collected and then returned in a dict, to be analyzed.

    Args:
        good_entities_file (str): path of the file where the good entities' log structured data is
        stored
        faulty_entities_file (str): path of the file where the faulty entities' log structured data
        is stored
        execution_id (str): id of the current execution

    Returns:
        dict: set with the parsed data for the 'good' and 'faulty' entities
    """

    sfl_logger.logger.info('Reading files: "%s" and "%s".',
                           good_entities_file, faulty_entities_file)
    good_entities: Set[Entity] = set()
    with open(good_entities_file, 'r', encoding='utf-8') as entities_file:

        for entity_line in entities_file:
            pm.parse_json_entity(entity_line)

        good_entities_filename = sfl_obj.extract_filename(
            good_entities_file)
        good_entities = pm.flush_mq_messages(
            good_entities_filename, execution_id)
        pm.clear_entities()

    faulty_entities: Set[Entity] = set()
    with open(faulty_entities_file, 'r', encoding='utf-8') as entities_file:

        for entity_line in entities_file:
            pm.parse_json_entity(entity_line)

        faulty_entities_filename = sfl_obj.extract_filename(
            faulty_entities_file)
        faulty_entities = pm.flush_mq_messages(
            faulty_entities_filename, execution_id)
        pm.clear_entities()

    sfl_logger.logger.info('Files reading complete.')
    return {good_entities_file: good_entities, faulty_entities_file: faulty_entities}
