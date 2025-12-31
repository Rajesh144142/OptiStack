from contextlib import contextmanager
from app.core.config import settings
from app.core.exceptions import DatabaseConnectionError
from influxdb_client import InfluxDBClient
from typing import Optional

_client: Optional[InfluxDBClient] = None

def get_influxdb_client() -> Optional[InfluxDBClient]:
    global _client
    if _client is not None:
        return _client
        
    if not settings.INFLUXDB_URL:
        return None
    
    _client = InfluxDBClient(
        url=settings.INFLUXDB_URL,
        token=settings.INFLUXDB_TOKEN or "",
        org=settings.INFLUXDB_ORG or "optistack",
        timeout=10000
    )
    return _client

@contextmanager
def get_influxdb_connection():
    client = get_influxdb_client()
    if not client:
        raise DatabaseConnectionError("InfluxDB connection not available")
    try:
        yield client
    except Exception as e:
        raise DatabaseConnectionError(f"InfluxDB operation failed: {e}") from e

def check_influxdb_health() -> bool:
    try:
        client = get_influxdb_client()
        if not client:
            return False
        client.ping()
        return True
    except Exception:
        return False

