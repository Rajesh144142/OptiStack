from app.models.experiment import Base
from app.db.postgres import get_postgres_async_engine
from sqlalchemy.ext.asyncio import AsyncSession

async def init_db():
    engine = get_postgres_async_engine()
    if engine:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

