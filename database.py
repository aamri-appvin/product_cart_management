from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import dotenv_values, load_dotenv
import os


credentials=dotenv_values(".env")


user = credentials.get("USER")
password = credentials.get("PASSWORD")
database = credentials.get("DATABASE")


if not all([user, password, database]):
    raise ValueError("Missing required environment variables: USER, PASSWORD, or DATABASE")


DATABASE_URL = f"postgresql+asyncpg://{user}:{password}@localhost/{database}"


engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()
