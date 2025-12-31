from redis.asyncio import Redis
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
            return config.get("databases", {}).get("redis", {})
    except Exception:
        return {}

async def get_redis_client():
    global _client
    if _client is not None:
        return _client
        
    if not settings.REDIS_URL:
        return None
    
    pool_config = _load_pool_config()
    max_connections = pool_config.get("max_connections", 50)
    
    _client = Redis.from_url(
        settings.REDIS_URL,
        max_connections=max_connections,
        socket_connect_timeout=5,
        socket_timeout=5,
        decode_responses=False
    )
    return _client

@asynccontextmanager
async def get_redis_connection():
    from app.core.exceptions import DatabaseConnectionError
    client = await get_redis_client()
    if not client:
        raise DatabaseConnectionError("Redis connection not available")
    try:
        yield client
    except Exception as e:
        raise DatabaseConnectionError(f"Redis operation failed: {e}") from e

async def check_redis_health() -> bool:
    try:
        client = await get_redis_client()
        if not client:
            return False
        await client.ping()
        return True
    except Exception:
        return False
