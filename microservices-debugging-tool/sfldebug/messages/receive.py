from typing import Callable
import multiprocessing as mp
import pika
from pika.channel import Channel

from sfldebug.messages.parse_message import parse_mq_message, flush_mq_messages


def setup_mq_channel(callback: Callable, host: str = 'localhost', exchange: str = 'logstash-output',
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
    channel.exchange = exchange  # Note: adding property to instance, not part of class

    result = channel.queue_declare(queue='')
    queue_name = result.method.queue

    # Bind the queue to receive logs from logstash with the appropriate routing key
    channel.queue_bind(exchange=exchange, queue=queue_name,
                       routing_key=routing_key)

    # Define the action upon receiving a message
    channel.basic_consume(
        queue=queue_name, on_message_callback=callback, auto_ack=True)

    return channel


def receive_mq_messages(queue: mp.Queue, callback: Callable, host: str = 'localhost',
                        exchange: str = 'logstash-output', routing_key: str = 'logstash-output'):
    """Start consuming messages from the channel, keeping it open until there is an interruption.

    Args:
        Args:
        queue (Queue): shared queue to store the received entities
        callback (callable): function to be called when a message is received (required)
        host (str): target to host to setup connection (default 'localhost')
        exchange (str): name of the mq exchange to setup connection (default 'logstash-output')
        routing_key (str): name of the routing key for the mq exchange (default 'logstash-output')
    """
    channel = setup_mq_channel(callback, host, exchange, routing_key)
    print('"{}" - Waiting for logs. To exit press CTRL+C'.format(channel.exchange))
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        # TODO improve communications interruption handling
        print('"{}" - Terminating connection!'.format(channel.exchange))
        channel.close()
        print('"{}" - Flushing messages collected'.format(channel.exchange))
        ret = queue.get()
        exec_id = ret['execution_id']
        ret[exchange] = flush_mq_messages(exchange, exec_id)
        queue.put(ret)


def receive_mq(good_entities_id: str, faulty_entities_id: str, execution_id: str) -> dict:
    """Receives log data through MQ channels.
    Each channel receives the messages and sends the data to a parser.
    The channels are set up in different processes for concurrent receival of messages.
    Returns a set with the parsed data for the 'good' and 'faulty' entities.

    Args:
        good_entities_id (str): name of the exchange where the good entities' log data will
        originate from
        faulty_entities_id (str): name of the exchange where the faulty entities' log data will
        originate from

    Returns:
        dict: set with the parsed data for the 'good' and 'faulty' entities
    """

    queue = mp.Queue()
    return_entities = {good_entities_id: set(), faulty_entities_id: set(),
                       'execution_id': execution_id}
    queue.put(return_entities)

    # Receive messages from both channel simultaneously, with multiprocessing
    good_receiver_process = mp.Process(
        target=receive_mq_messages, args=(queue, parse_mq_message),
        kwargs={'exchange': good_entities_id, 'routing_key': good_entities_id})

    faulty_receiver_process = mp.Process(
        target=receive_mq_messages, args=(queue, parse_mq_message),
        kwargs={'exchange': faulty_entities_id, 'routing_key': faulty_entities_id})

    try:
        good_receiver_process.start()
        faulty_receiver_process.start()
        good_receiver_process.join()
        faulty_receiver_process.join()
    except KeyboardInterrupt:
        # TODO improve error handling
        return queue.get()
