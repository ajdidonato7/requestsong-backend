from pymongo import MongoClient
from pymongo.database import Database
from app.config import settings

class MongoDB:
    client: MongoClient = None
    database: Database = None

mongodb = MongoDB()

def connect_to_mongo():
    """Create database connection"""
    mongodb.client = MongoClient(settings.MONGODB_URL)
    mongodb.database = mongodb.client[settings.DATABASE_NAME]
    
    # Create indexes for better performance
    # Index on artist username for faster lookups
    mongodb.database.artists.create_index("username", unique=True)
    mongodb.database.artists.create_index("email", unique=True)
    
    # Index on requests for faster queries
    mongodb.database.requests.create_index([("artist_username", 1), ("queue_position", 1)])
    mongodb.database.requests.create_index([("artist_username", 1), ("status", 1)])
    mongodb.database.requests.create_index("created_at")

def close_mongo_connection():
    """Close database connection"""
    if mongodb.client:
        mongodb.client.close()

def get_database() -> Database:
    """Get database instance"""
    return mongodb.database