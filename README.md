Notification Cluster API
Overview
This project implements a scalable Notification Service using FastAPI, MongoDB, and RabbitMQ, ensuring reliable delivery of notifications to users. The architecture is designed for efficiency, with message queuing for asynchronous processing and retry mechanisms for failed notifications.
Features
- RESTful API Endpoints for sending and retrieving notifications.
- Supports multiple notification types: Email, SMS, and In-App.
- RabbitMQ Integration for queue-based processing.
- MongoDB for persistence and retrieval of notifications.
- Retry Mechanism to handle failures.

Tech Stack
This project leverages the following technologies:
| Technology | Purpose | 
| FastAPI | Web framework for building APIs | 
| MongoDB | Database for storing notifications | 
| RabbitMQ | Message broker for asynchronous processing | 
| Pydantic | Data validation | 
| Uvicorn | ASGI server | 
| Docker (Optional) | Containerized deployment | 

Setup Instructions
1️⃣ Prerequisites
Ensure you have the following installed:
- Python 3.7+
- MongoDB (Local or Cloud)
- RabbitMQ (Local or Cloud)
- Render (For deployment, optional)

2️⃣ Clone the Repository
git clone <repository-url>
cd notification-cluster-api

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Set Environment Variables
Create a .env file with:
MONGODB_URI=<your-mongodb-uri>
RABBITMQ_URL=<your-rabbitmq-url>

Alternatively, set them in the terminal:
export MONGODB_URI="<your-mongodb-uri>"
export RABBITMQ_URL="<your-rabbitmq-url>"

5️⃣ Run API Service
Start the FastAPI server:
uvicorn app.main:app --host 0.0.0.0 --port 10000

6️⃣ Run the Worker Service
Start the RabbitMQ consumer:
python worker/consumer.py

7️⃣ Test MongoDB Connection
python test_mongo_connection.py

API Endpoints
POST /notifications → Send a notification
Example Request

{
  "user_id": "user123",
  "message": "Welcome to the service!",
  "notification_type": "email"
}

Example cURL

curl -X POST "http://localhost:10000/notifications" \
    -H "Content-Type: application/json" \
    -d '{"user_id": "user123", "message": "Welcome!", "notification_type": "email"}'

GET /users/{user_id}/notifications → Retrieve user notifications
Example Response

{
  "notifications": [
    {
      "id": "664f6a2e9b982cbb7d4a8b56",
      "message": "Welcome to the service!",
      "type": "email"
    }
  ]
}

Example cURL
curl -X GET "http://localhost:10000/users/user123/notifications" \
    -H "accept: application/json"

Architecture
This system is structured as follows:
📌 API Layer (FastAPI)
- Handles incoming requests.
- Validates and queues notifications.
📌 Worker Layer (RabbitMQ Consumer)
- Consumes notifications from the queue.
- Saves them in MongoDB.
📌 Database Layer (MongoDB)
- Stores notifications for retrieval

Deployment
🚀 Render Deployment (render.yaml)
This project uses Render for cloud deployment. The configuration in render.yaml defines:
- API service (notification-api) running FastAPI.
- Worker service (notification-worker) processing notifications.
Deploy using:
git push origin master

Error Handling & Retries
- If a notification fails to process, the consumer.py script retries after 5 seconds.
- Failed notifications are requeued in RabbitMQ.

Assumptions
- MongoDB and RabbitMQ are running correctly.
- Only three notification types are supported: Email, SMS, and In-App.
- The project assumes environment variables are correctly set.

Future Improvements
- Kafka-based event streaming for large-scale notification handling.
- Rate limiting to prevent abuse of the API.
- User authentication for secured API access.

Conclusion
This project demonstrates a scalable notification system, integrating FastAPI, MongoDB, and RabbitMQ for efficient queue-based processing. It highlights key principles of asynchronous messaging, reliability, and fault tolerance.
