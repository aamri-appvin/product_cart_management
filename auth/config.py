from pydantic_settings import BaseSettings
from dotenv import dotenv_values

credentials = dotenv_values(".env")

class Settings(BaseSettings):
    DATABASE_URL: str = f'postgresql+asyncpg://{credentials.get("USER")}:{credentials.get("PASSWORD")}@localhost/{credentials.get("DATABASE")}'
    SECRET_KEY: str = credentials.get("SECRET_KEY")
    ALGORITHM: str = credentials.get("ALGORITHM")
    TOKEN_EXPIRY_TIME: int = int(credentials.get("TOKEN_EXPIRY_TIME"))

settings = Settings()
