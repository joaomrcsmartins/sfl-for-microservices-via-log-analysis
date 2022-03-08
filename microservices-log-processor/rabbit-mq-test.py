import pika, json

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='logstash-output', exchange_type='direct', durable=True)

result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

channel.queue_bind(exchange='logstash-output', queue=queue_name, routing_key='logstash-output')

print('Waiting for logs. To exit press CTRL+C')

def callback(ch, method, properties, body):
    json_body = json.loads(body)
    print(json.dumps(json_body, indent=2, sort_keys=True))

channel.basic_consume(
    queue=queue_name, on_message_callback=callback, auto_ack=True)

channel.start_consuming()