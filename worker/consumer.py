import pika
import json
from pymongo import MongoClient
import os
import time
import certifi

# Setup MongoDB
MONGO_URI = os.getenv("MONGODB_URI")
client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client["notification_db"]
notifications_collection = db["notifications"]

# Setup RabbitMQ
RABBITMQ_URL = os.getenv("RABBITMQ_URL")
params = pika.URLParameters(RABBITMQ_URL)
connection = pika.BlockingConnection(params)
channel = connection.channel()
channel.queue_declare(queue='notification_queue', durable=True)

def callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        notifications_collection.insert_one(data)
        print("Notification saved:", data)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print("Error:", e)
        time.sleep(5)
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='notification_queue', on_message_callback=callback)
print(" [*] Waiting for messages.")

# Ensure the consumer only starts when executed directly
if __name__ == "__main__":
    print(" [*] Starting consumer...")
    channel.start_consuming()