from pydantic_settings import BaseSettings
import secrets

class Settings(BaseSettings):
    DATABASE_URL:str='postgresql+asyncpg://myuser:NewPassword123!@localhost/new_db'
    SECRET_KEY:str=secrets.token_urlsafe(64)
    ALGORITHM:str="HS256"
    TOKEN_EXPIRY_TIME:int=30

settings=Settings()