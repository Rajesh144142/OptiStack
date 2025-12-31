from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager
from app.core.config import settings
import yaml
import os

_client = None

def _load_pool_config():
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "conf", "config.yaml")
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            return config.get("databases", {}).get("mongodb", {})
    except Exception:
        return {}

def get_mongodb_client():
    global _client
    if _client is not None:
        return _client
        
    if not settings.MONGODB_URL:
        return None
    
    pool_config = _load_pool_config()
    max_pool_size = pool_config.get("max_pool_size", 50)
    
    _client = AsyncIOMotorClient(
        settings.MONGODB_URL,
        maxPoolSize=max_pool_size,
        serverSelectionTimeoutMS=5000
    )
    return _client

def get_mongodb_database(db_name: str = "optistack"):
    client = get_mongodb_client()
    if not client:
        return None
    return client[db_name]

@asynccontextmanager
async def get_mongodb_connection(db_name: str = "optistack"):
    from app.core.exceptions import DatabaseConnectionError
    client = get_mongodb_client()
    if not client:
        raise DatabaseConnectionError("MongoDB connection not available")
    try:
        yield client[db_name]
    except Exception as e:
        raise DatabaseConnectionError(f"MongoDB operation failed: {e}") from e

async def check_mongodb_health() -> bool:
    try:
        client = get_mongodb_client()
        if not client:
            return False
        await client.admin.command('ping')
        return True
    except Exception:
        return False
