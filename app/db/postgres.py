from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from contextlib import asynccontextmanager
from app.core.config import settings
import yaml
import os
import asyncio

_async_engine = None
_AsyncSessionLocal = None

_sync_engine = None
_SessionLocal = None

def _load_pool_config():
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "conf", "config.yaml")
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            return config.get("databases", {}).get("postgres", {})
    except Exception:
        return {}

def get_postgres_async_engine():
    global _async_engine
    if _async_engine is not None:
        return _async_engine
        
    if not settings.POSTGRES_HOST:
        return None
    
    pool_config = _load_pool_config()
    pool_size = pool_config.get("pool_size", 10)
    
    database_url = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    _async_engine = create_async_engine(
        database_url,
        pool_size=pool_size,
        max_overflow=0,
        pool_pre_ping=True,
        echo=False
    )
    return _async_engine

def get_postgres_async_session():
    global _AsyncSessionLocal
    if _AsyncSessionLocal is None:
        engine = get_postgres_async_engine()
        if not engine:
            return None
        _AsyncSessionLocal = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    return _AsyncSessionLocal()

@asynccontextmanager
async def get_postgres_connection():
    from app.core.exceptions import DatabaseConnectionError
    session = get_postgres_async_session()
    if not session:
        raise DatabaseConnectionError("PostgreSQL connection not available")
    try:
        yield session
    except Exception as e:
        await session.rollback()
        raise DatabaseConnectionError(f"PostgreSQL operation failed: {e}") from e
    finally:
        await session.close()

async def check_postgres_health() -> bool:
    try:
        engine = get_postgres_async_engine()
        if not engine:
            return False
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False

def get_postgres_engine():
    global _sync_engine
    if _sync_engine is not None:
        return _sync_engine
        
    if not settings.POSTGRES_HOST:
        return None
    
    from sqlalchemy import create_engine
    from sqlalchemy.pool import QueuePool
    
    pool_config = _load_pool_config()
    pool_size = pool_config.get("pool_size", 10)
    max_overflow = pool_config.get("max_overflow", 20)
    
    database_url = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    _sync_engine = create_engine(
        database_url,
        poolclass=QueuePool,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_pre_ping=True
    )
    return _sync_engine

def get_postgres_session():
    global _SessionLocal
    if _SessionLocal is None:
        from sqlalchemy.orm import sessionmaker
        engine = get_postgres_engine()
        if not engine:
            return None
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return _SessionLocal()
