from logging.config import fileConfig
from sqlalchemy import pool, create_engine
from alembic import context

import sys
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from app.db.session import Base
from app.db.models import *  # noqa
from app.core.config import settings

config = context.config
target_metadata = Base.metadata


def _strip_query(url: str) -> str:
    if not url:
        return url
    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", parts.fragment))


def _sync_dsn() -> str:
    url = _strip_query(settings.DATABASE_URL or "")
    return url.replace("postgresql+asyncpg://", "postgresql://")


def run_migrations_offline():
    url = _sync_dsn()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        transaction_per_migration=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    engine = create_engine(
        _sync_dsn(),
        poolclass=pool.NullPool,
        connect_args={"sslmode": "require"},
    )
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            transaction_per_migration=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
