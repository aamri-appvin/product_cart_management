from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import *
from schema import *
from models import Product
import models
import Exception
from auth import utils

#Auth Operations
async def user_signup(user: User_Model, db: AsyncSession):
    print("User Signup")

    result = await db.execute(
        select(Users).filter(
            Users.email == user.email,
        )
    )
    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(status_code=Exception.CONFLICT.status_code, detail="EMAIL ALREADY EXISTS")

    new_item = Users(
        name=user.name,
        email=user.email,
        password=await utils.get_password_hash(user.password),
    )
    db.add(new_item)
    await db.commit()
    await db.refresh(new_item)
    return {
        "id": new_item.id,
        "name": new_item.name,
        "email": new_item.email
    }

async def user_login(user:User_Model,db:AsyncSession):
    existing_user = await db.execute(
        select(Users).filter(
            Users.email == user.email,
        )
    )
    existing_user=existing_user.scalars().first()

    if not existing_user or not await utils.verify_password(user.password,existing_user.password):
        raise HTTPException(status_code=Exception.UNAUTHORIZED.status_code,detail=str("INVALID CREDENTIALS"))
    access_token=await utils.create_access_token(data={"email":existing_user.email})
    name_user = await db.execute(
        select(Users).filter(
            Users.name== user.name,
        )
    )
    name_user=name_user.scalars().first()
    if not name_user:
        raise HTTPException(status_code=Exception.UNAUTHORIZED.status_code,detail=str("INCORRECT NAME PROVIDED"))
    return {"access_token":access_token,"token_type":"bearer"}
