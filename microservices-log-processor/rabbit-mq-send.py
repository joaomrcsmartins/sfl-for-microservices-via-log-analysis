import pika, os

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

# extracted from https://www.ibm.com/docs/en/zos/2.1.0?topic=problems-example-log-file
with open(os.path.join(__location__, 'data/rabbitmq/ibmlogexamples.log'),'r') as log_file:

    channel.exchange_declare(exchange='logstash-input', exchange_type='direct')

    for line in log_file.readlines():
        channel.basic_publish(exchange='logstash-input', routing_key='logstash-input', body=line)
        print("Sent :: %r" % line)

    connection.close()