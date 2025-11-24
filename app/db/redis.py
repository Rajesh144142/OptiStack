import redis
from app.core.config import settings

def get_redis_client():
    if not settings.REDIS_URL:
        return None
    return redis.from_url(settings.REDIS_URL)

