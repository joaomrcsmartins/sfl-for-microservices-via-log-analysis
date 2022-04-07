# pylint: disable=C0111
"""Dummy sender that sends log formatted data, acting as logstash output"""
import os
import multiprocessing as mp
import json
import pika

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))


def dummy_sender(filename: str, exchange: str):

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    with open(os.path.join(__location__, filename), 'r', encoding='utf-8') as log_file:

        channel.exchange_declare(exchange=exchange,
                                 exchange_type='direct', durable=True)

        data = json.load(log_file)

        for log in data:
            channel.basic_publish(exchange=exchange,
                                  routing_key=exchange, body=json.dumps(log))
            print('Sent :: {}'.format(json.dumps(log)))
        connection.close()


if __name__ == '__main__':
    first_sender = mp.Process(
        target=dummy_sender, args=('dummy_log_hierarchy.json', 'logstash-output-good',))
    second_sender = mp.Process(
        target=dummy_sender, args=('dummy_log_data.json', 'logstash-output-bad',))

    first_sender.start()
    second_sender.start()
    first_sender.join()
    second_sender.join()
