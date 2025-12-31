from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from contextlib import asynccontextmanager
from app.core.config import settings
import yaml
import os

_async_engine = None
_AsyncSessionLocal = None

def _load_pool_config():
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "conf", "config.yaml")
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            return config.get("databases", {}).get("cockroachdb", {})
    except Exception:
        return {}

def get_cockroachdb_async_engine():
    global _async_engine
    if _async_engine is not None:
        return _async_engine
        
    if not settings.COCKROACHDB_HOST:
        return None
    
    pool_config = _load_pool_config()
    pool_size = pool_config.get("pool_size", 10)
    
    user = settings.COCKROACHDB_USER or "root"
    password = settings.COCKROACHDB_PASSWORD or ""
    auth = f"{user}:{password}@" if password else f"{user}@"
    database_url = f"postgresql+asyncpg://{auth}{settings.COCKROACHDB_HOST}:{settings.COCKROACHDB_PORT}/{settings.COCKROACHDB_DB}?sslmode=disable"
    
    _async_engine = create_async_engine(
        database_url,
        pool_size=pool_size,
        max_overflow=0,
        pool_pre_ping=True,
        echo=False
    )
    return _async_engine

def get_cockroachdb_async_session():
    global _AsyncSessionLocal
    if _AsyncSessionLocal is None:
        engine = get_cockroachdb_async_engine()
        if not engine:
            return None
        _AsyncSessionLocal = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    return _AsyncSessionLocal()

@asynccontextmanager
async def get_cockroachdb_connection():
    from app.core.exceptions import DatabaseConnectionError
    session = get_cockroachdb_async_session()
    if not session:
        raise DatabaseConnectionError("CockroachDB connection not available")
    try:
        yield session
    except Exception as e:
        await session.rollback()
        raise DatabaseConnectionError(f"CockroachDB operation failed: {e}") from e
    finally:
        await session.close()

async def check_cockroachdb_health() -> bool:
    try:
        engine = get_cockroachdb_async_engine()
        if not engine:
            return False
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
