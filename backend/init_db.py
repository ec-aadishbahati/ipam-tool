from app.db.session import engine, Base
from app.db.models import user, supernet, subnet, device, purpose
import asyncio

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print('Database tables created successfully')

if __name__ == "__main__":
    asyncio.run(create_tables())
