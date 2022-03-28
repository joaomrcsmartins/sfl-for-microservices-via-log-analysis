# pylint: disable=C0111
import json
import pika

# Open connection in localhost
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

# Define the exchange, the name of the exchange in the logstash config, and the appropriate params
# By default logstash creates durable exchanges
channel.exchange_declare(exchange='logstash-output',
                         exchange_type='direct', durable=True)

result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

# Bind the queue to receive logs from logstash with the appropriate routing key
channel.queue_bind(exchange='logstash-output',
                   queue=queue_name, routing_key='logstash-output')
print('Waiting for logs. To exit press CTRL+C')

# Open log file to store messages received from logstash
logfile = open('logstash-rabbitmq.json', 'w', encoding='utf-8')
json_logfile = {"logs": []}

# Callback when a message is received, prints the logs in stdout and writes to the log file


def callback(cha, method, properties, body):
    del cha, method, properties
    json_body = json.loads(body)
    json_logfile['logs'].append(json_body)


channel.basic_consume(
    queue=queue_name, on_message_callback=callback, auto_ack=True)

try:
    channel.start_consuming()
except KeyboardInterrupt:  # Close the file when CTRL+C is pressed or there is a error
    logfile.write(json.dumps(json_logfile, indent=2, sort_keys=True))
    logfile.close()
except OSError:
    logfile.close()
