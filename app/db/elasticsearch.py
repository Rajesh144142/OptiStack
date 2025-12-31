from contextlib import contextmanager
from app.core.config import settings
from app.core.exceptions import DatabaseConnectionError
from elasticsearch import Elasticsearch
from typing import Optional

_client: Optional[Elasticsearch] = None

def get_elasticsearch_client() -> Optional[Elasticsearch]:
    global _client
    if _client is not None:
        return _client
        
    if not settings.ELASTICSEARCH_URL:
        return None
    
    auth = None
    if settings.ELASTICSEARCH_USER and settings.ELASTICSEARCH_PASSWORD:
        auth = (settings.ELASTICSEARCH_USER, settings.ELASTICSEARCH_PASSWORD)
    
    _client = Elasticsearch(
        [settings.ELASTICSEARCH_URL],
        basic_auth=auth,
        request_timeout=30
    )
    return _client

@contextmanager
def get_elasticsearch_connection():
    client = get_elasticsearch_client()
    if not client:
        raise DatabaseConnectionError("Elasticsearch connection not available")
    try:
        yield client
    except Exception as e:
        raise DatabaseConnectionError(f"Elasticsearch operation failed: {e}") from e

def check_elasticsearch_health() -> bool:
    try:
        client = get_elasticsearch_client()
        if not client:
            return False
        return client.ping()
    except Exception:
        return False

