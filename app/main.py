from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, EmailStr
from enum import Enum
from typing import Optional
from pymongo import MongoClient
from bson import ObjectId
from starlette.responses import RedirectResponse
import os
import pika
import json
import uuid
import certifi
import secrets

app = FastAPI()
security = HTTPBasic()

# MongoDB setup
MONGO_URI = os.getenv("MONGODB_URI")
if not MONGO_URI:
    raise RuntimeError("MONGODB_URI environment variable not set")

try:
    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000,
        tlsCAFile=certifi.where()
    )
    db = client["notification_db"]
    notifications_collection = db["notifications"]
    client.admin.command('ping')
except Exception as e:
    raise RuntimeError(f"Failed to connect to MongoDB: {str(e)}")

# Enum for notification types
class NotificationType(str, Enum):
    email = "email"
    sms = "sms"
    in_app = "in_app"

# Pydantic model for request
class Notification(BaseModel):
    from_: EmailStr
    to: EmailStr
    message: str
    notification_type: NotificationType
    encoding: str = "utf-8"

# Basic Auth validator
def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    expected_username = os.getenv("BASIC_AUTH_USERNAME", "admin")
    expected_password = os.getenv("BASIC_AUTH_PASSWORD", "secret")
    correct_username = secrets.compare_digest(credentials.username, expected_username)
    correct_password = secrets.compare_digest(credentials.password, expected_password)

    if not (correct_username and correct_password):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return credentials.username

@app.get("/", include_in_schema=False)
def redirect_to_docs():
    return RedirectResponse(url="/docs")

@app.post("/notifications")
def send_notification(notification: Notification, _: str = Depends(authenticate)):
    RABBITMQ_URL = os.getenv("RABBITMQ_URL")
    if not RABBITMQ_URL:
        raise HTTPException(status_code=500, detail="RABBITMQ_URL not set")

    transaction_id = str(uuid.uuid4())
    message = notification.dict()
    message["transaction_id"] = transaction_id

    try:
        connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
        channel = connection.channel()
        channel.queue_declare(queue='notification_queue', durable=True)

        channel.basic_publish(
            exchange='',
            routing_key='notification_queue',
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2),
        )
        connection.close()

        return {"transaction_id": transaction_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to publish message: {str(e)}")

@app.get("/notifications/status")
def get_notification_status(
    transaction_id: str = Query(..., description="Transaction ID"),
    _: str = Depends(authenticate)
):
    try:
        result = notifications_collection.find_one({"transaction_id": transaction_id})
        if result:
            return {
                "transaction_id": result["transaction_id"],
                "status": "stored",
                "to": result["to"],
                "type": result["notification_type"]
            }
        else:
            raise HTTPException(status_code=404, detail="Notification not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch notification: {str(e)}")
