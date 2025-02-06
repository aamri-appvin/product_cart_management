from dotenv import dotenv_values
from fastapi import FastAPI, HTTPException, status, Depends
from jose import JWTError, jwt
from auth.config import settings
# from fastapi.security import OAuth2PasswordBearer 
#TOKEN AUTHORIZATION
from functools import wraps

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

cred=dotenv_values(".env")
app = FastAPI()

from fastapi import HTTPException, Depends, Header
from jose import JWTError, jwt
from datetime import datetime, timedelta
from auth.config import settings


def get_token_from_header(authorization: str = Header(...)):
    print("authorization..........",authorization)
    if authorization and authorization.startswith("Bearer "):
        print(authorization[7:] )
        return authorization[7:] 
    raise HTTPException(status_code=401, detail="Bearer token missing")


async def secure_endpoint(token: str = Depends(get_token_from_header)):
    print("Your Token is ",token[7:])
    try:
        payload = jwt.decode(token[7:], settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("email")
        print(payload)
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return email  
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid credentials")

