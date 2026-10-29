from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


from tag7.db import url


async_url = url.set(drivername="mysql+aiomysql")
async_engine = create_async_engine(
    async_url,
    pool_pre_ping=True,
    connect_args={"connect_timeout": 5}
)


AsyncSessionLocal = async_sessionmaker(async_engine, expire_on_commit=False)

async def get_async_session() -> AsyncIterator[AsyncSession]:
    async with AsyncSessionLocal() as db:
        yield db




AsyncDb = Annotated[AsyncSession, Depends(get_async_session)]