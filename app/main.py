from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from pymongo import MongoClient
from bson import ObjectId
import os
import pika
import json

app = FastAPI()

# MongoDB setup
MONGO_URI = os.getenv("MONGODB_URI")
if not MONGO_URI:
    raise RuntimeError("MONGODB_URI environment variable not set")
client = MongoClient(MONGO_URI)
db = client["notification_db"]
notifications_collection = db["notifications"]

<<<<<<< HEAD
=======
# RabbitMQ setup
RABBITMQ_URL = os.getenv("RABBITMQ_URL")
if not RABBITMQ_URL:
    raise RuntimeError("RABBITMQ_URL environment variable not set")
params = pika.URLParameters(RABBITMQ_URL)
connection = pika.BlockingConnection(params)
channel = connection.channel()
channel.queue_declare(queue='notification_queue', durable=True)

>>>>>>> aaa80f6c01d1e39e60664a3c1ad15db64b1dbb86
# Pydantic models
class Notification(BaseModel):
    user_id: str
    message: str
    notification_type: str  # email, sms, in-app

@app.post("/notifications")
def send_notification(notification: Notification):
    RABBITMQ_URL = os.getenv("RABBITMQ_URL")
    if not RABBITMQ_URL:
        raise HTTPException(status_code=500, detail="RABBITMQ_URL not set")

    try:
        connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
        channel = connection.channel()
        channel.queue_declare(queue='notification_queue', durable=True)

        message = notification.dict()
        channel.basic_publish(
            exchange='',
            routing_key='notification_queue',
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2),
        )
        connection.close()
        return {"status": "queued"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to publish message: {str(e)}")

@app.get("/users/{user_id}/notifications")
def get_user_notifications(user_id: str):
    results = notifications_collection.find({"user_id": user_id})
    notifications = [
        {"id": str(n["_id"]), "message": n["message"], "type": n["notification_type"]}
        for n in results
    ]
    return {"notifications": notifications}
