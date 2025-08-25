import asyncio
import os
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app.db.models.user import User
from app.core.security import get_password_hash


ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "changeme123!")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@example.com")


async def ensure_columns(session: AsyncSession) -> None:
    res = await session.execute(
        text("SELECT column_name FROM information_schema.columns WHERE table_name='users'")
    )
    cols = {row[0] for row in res.fetchall()}
    if "email" not in cols:
        await session.execute(text("ALTER TABLE users ADD COLUMN email VARCHAR(255)"))
        await session.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_email ON users (email)"))
    if "hashed_password" not in cols:
        await session.execute(text("ALTER TABLE users ADD COLUMN hashed_password VARCHAR(255)"))
    if "is_admin" not in cols:
        await session.execute(text("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT false NOT NULL"))
    await session.commit()


async def ensure_admin() -> None:
    async with AsyncSessionLocal() as session:
        await ensure_columns(session)
        q = select(User).where(User.email == ADMIN_EMAIL)
        res = await session.execute(q)
        user = res.scalar_one_or_none()
        if user is None:
            user = User(
                email=ADMIN_EMAIL,
                hashed_password=get_password_hash(ADMIN_PASSWORD),
                is_admin=True,
            )
            session.add(user)
            await session.commit()


if __name__ == "__main__":
    asyncio.run(ensure_admin())
