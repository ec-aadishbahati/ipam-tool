import asyncio
from passlib.context import CryptContext
from app.db.session import AsyncSessionLocal
from app.db.models.user import User
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_admin_user():
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select
        result = await session.execute(select(User).where(User.email == settings.ADMIN_EMAIL))
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            print(f"Admin user {settings.ADMIN_EMAIL} already exists")
            return
        
        hashed_password = pwd_context.hash(settings.ADMIN_PASSWORD)
        admin_user = User(
            email=settings.ADMIN_EMAIL,
            hashed_password=hashed_password,
            is_admin=True
        )
        
        session.add(admin_user)
        await session.commit()
        print(f"Admin user {settings.ADMIN_EMAIL} created successfully")

if __name__ == "__main__":
    asyncio.run(create_admin_user())
