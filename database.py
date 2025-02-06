from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import dotenv_values
import os


credentials = dotenv_values(".env")

user = credentials.get("USER")
password = credentials.get("PASSWORD")
database = credentials.get("DATABASE")
db_port = credentials.get("DB_PORT")

DATABASE_URL = f"postgresql+asyncpg://{user}:{password}@localhost:5432/{database}"

engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()
