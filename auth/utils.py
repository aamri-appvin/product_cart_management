from sqlalchemy.ext.asyncio import AsyncSession
from auth import config
from jose import jwt 
from passlib.context import CryptContext
from datetime import datetime , timedelta
from utils.Response import generate_error_response,generate_success_response
from datetime import datetime, timedelta
from jose import jwt
from auth.config import settings

pwd_context = CryptContext(schemes=['bcrypt'], deprecated="auto")

async def get_password_hash(password:str):
    print("New Password!!!! YAYYYYYY")
    return pwd_context.hash(password)


async def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.TOKEN_EXPIRY_TIME)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def verify_password(user_password:str,db_hashed_password:str):
    return pwd_context.verify(user_password,db_hashed_password)



