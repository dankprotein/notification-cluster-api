from pymongo import MongoClient
import os

MONGODB_URI = os.getenv("MONGODB_URI") 

def test_connection():
    try:
        client = MongoClient(MONGODB_URI)
        db_names = client.list_database_names()
        print("✅ Connected successfully. Databases:", db_names)
    except Exception as e:
        print("❌ Connection failed:", e)

if __name__ == "__main__":
    test_connection()
