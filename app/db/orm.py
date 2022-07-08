import os

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

Engine = create_async_engine(
    f"postgresql+asyncpg://{os.environ['DB_URL']}",
    echo=False,
    future=True,
    pool_size=20,
    max_overflow=10
)

Session = sessionmaker(Engine, expire_on_commit=False, class_=AsyncSession)
