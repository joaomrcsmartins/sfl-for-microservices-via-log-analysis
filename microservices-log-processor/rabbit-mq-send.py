import pika
import sys

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='logstash', exchange_type='fanout',durable=True)

message = ' '.join(sys.argv[1:]) or "info: Hello World!"
channel.basic_publish(exchange='logstash', routing_key='', body=message)
print("Sent - [%r]" % message)
connection.close()