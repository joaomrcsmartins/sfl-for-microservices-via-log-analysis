"""Dummy sender that sends log formatted data, acting as logstash output"""
import os
import json
import pika

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

with open(os.path.join(__location__, 'dummy_log_data.json'), 'r', encoding='utf-8') as log_file:

    channel.exchange_declare(exchange='logstash-output',
                             exchange_type='direct', durable=True)

    data = json.load(log_file)

    for log in data:
        channel.basic_publish(exchange='logstash-output',
                              routing_key='logstash-output', body=json.dumps(log))
        print('Sent :: {}'.format(json.dumps(log)))

    connection.close()
