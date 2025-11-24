from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

def get_cockroachdb_engine():
    if not settings.COCKROACHDB_HOST:
        return None
    user = settings.COCKROACHDB_USER or "root"
    password = settings.COCKROACHDB_PASSWORD or ""
    auth = f"{user}:{password}@" if password else f"{user}@"
    database_url = f"postgresql://{auth}{settings.COCKROACHDB_HOST}:{settings.COCKROACHDB_PORT}/{settings.COCKROACHDB_DB}?sslmode=disable"
    return create_engine(database_url)

def get_cockroachdb_session():
    engine = get_cockroachdb_engine()
    if not engine:
        return None
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

