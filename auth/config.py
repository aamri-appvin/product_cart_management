from pydantic_settings import BaseSettings
import secrets
from dotenv import dotenv_values

credentials=dotenv_values(".env")

class Settings(BaseSettings):
    DATABASE_URL: str = f'postgresql+asyncpg://{credentials.get("USER")}:{credentials.get("PASSWORD")}@localhost/{credentials.get("DATABASE")}'
    SECRET_KEY:str=secrets.token_urlsafe(64)
    ALGORITHM:str="HS256"
    TOKEN_EXPIRY_TIME:int=30

settings=Settings()