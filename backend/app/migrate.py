import asyncio
import subprocess
import sys
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import engine


async def main() -> int:
    proc = subprocess.run(["alembic", "upgrade", "head"], check=False)
    return proc.returncode


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
