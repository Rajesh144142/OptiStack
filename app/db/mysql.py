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
            return config.get("databases", {}).get("mysql", {})
    except Exception:
        return {}

def get_mysql_async_engine():
    global _async_engine
    if _async_engine is not None:
        return _async_engine
        
    if not settings.MYSQL_HOST:
        return None
    
    pool_config = _load_pool_config()
    pool_size = pool_config.get("pool_size", 10)
    
    database_url = f"mysql+aiomysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DB}"
    _async_engine = create_async_engine(
        database_url,
        pool_size=pool_size,
        max_overflow=0,
        pool_pre_ping=True,
        echo=False
    )
    return _async_engine

def get_mysql_async_session():
    global _AsyncSessionLocal
    if _AsyncSessionLocal is None:
        engine = get_mysql_async_engine()
        if not engine:
            return None
        _AsyncSessionLocal = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    return _AsyncSessionLocal()

@asynccontextmanager
async def get_mysql_connection():
    from app.core.exceptions import DatabaseConnectionError
    session = get_mysql_async_session()
    if not session:
        raise DatabaseConnectionError("MySQL connection not available")
    try:
        yield session
    except Exception as e:
        await session.rollback()
        raise DatabaseConnectionError(f"MySQL operation failed: {e}") from e
    finally:
        await session.close()

async def check_mysql_health() -> bool:
    try:
        engine = get_mysql_async_engine()
        if not engine:
            return False
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
