from pymongo import MongoClient
from app.core.config import settings

def get_mongodb_client():
    if not settings.MONGODB_URL:
        return None
    return MongoClient(settings.MONGODB_URL)

def get_mongodb_database(db_name: str = None):
    client = get_mongodb_client()
    if not client:
        return None
    return client[db_name] if db_name else client.get_default_database()

