from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine
from pydantic_settings import BaseSettings
from app.models import user, family_member


class DataBaseSettings(BaseSettings):
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = DataBaseSettings()

DATABASE_URL = (
    f"mysql+aiomysql://{settings.DB_USER}:"
    f"{settings.DB_PASSWORD}@"
    f"{settings.DB_HOST}:"
    f"{settings.DB_PORT}/"
    f"{settings.DB_NAME}"
)

engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # shows SQL logs
)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


#Create a DB session dependency
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker

# This gives you:
# one DB session per request
# proper async handling

async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session