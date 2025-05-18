# Notification Cluster

This is a backend service to send and retrieve notifications via Email, SMS, and In-App.

## Features

- REST API built with FastAPI
- MongoDB integration
- RabbitMQ for asynchronous message processing
- Retry logic via queue
- Dockerized deployment-ready

## API Endpoints

- `POST /notifications`: Queue a new notification
- `GET /users/{user_id}/notifications`: Get all notifications for a user

## Setup

1. Set environment variables:

```
MONGODB_URI=<your-mongodb-uri>
RABBITMQ_URL=<your-rabbitmq-url>
ENV=production
```

2. Run worker:
```
python worker/consumer.py
```

3. Start API (Docker or directly):
```
gunicorn app.main:app --bind 0.0.0.0:8000
```