from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Fetch database credentials
user = os.getenv("USER")
password = os.getenv("PASSWORD")
database = os.getenv("DATABASE")

if not all([user, password, database]):
    raise ValueError("Missing required environment variables: USER, PASSWORD, or DATABASE")

# Construct the database URL
DATABASE_URL = f"postgresql+asyncpg://myuser:{password}@localhost/{database}"

# Create the async engine and session
engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

# Dependency to get the database session
async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()
