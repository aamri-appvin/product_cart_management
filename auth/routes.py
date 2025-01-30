from datetime import timedelta
import random
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import *
from schema import *
from models import Product
import models
from utils import Exception
from auth import utils
from utils.Response import generate_error_response,generate_success_response
import smtplib
from email.message import EmailMessage
from dotenv import dotenv_values
from random import randint
from mailjet_rest import Client
from random import randint
import os


GEN_OTP=None
EXP=None
credentials=dotenv_values(".env")
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
        return generate_error_response(Exception.CONFLICT.get("status_code"),"EMAIL ALREADY EXISTS",Exception.CONFLICT.get("detail"))
        # raise HTTPException(status_code=Exception.CONFLICT.status_code, detail="EMAIL ALREADY EXISTS")

    new_item = Users(
        name=user.name,
        email=user.email,
        password=await utils.get_password_hash(user.password),
    )
    db.add(new_item)
    await db.commit()
    await db.refresh(new_item)
    data={
        "id": new_item.id,
        "name": new_item.name,
        "email": new_item.email
    }
    return generate_success_response(status_code=200,message=f"{new_item.name} Signed Up Successfully",data=data)

async def user_login(user:User_Model,db:AsyncSession):
    existing_user = await db.execute(
        select(Users).filter(
            Users.email == user.email,
        )
    )
    existing_user=existing_user.scalars().first()

    if not existing_user or not await utils.verify_password(user.password,existing_user.password):
        return generate_error_response(Exception.UNAUTHORIZED.get("status_code"),"INVALID CREDENTIALS",Exception.UNAUTHORIZED.get("detail"))
        # raise HTTPException(status_code=Exception.UNAUTHORIZED.status_code,detail=str("INVALID CREDENTIALS"))
    access_token=await utils.create_access_token(data={"email":existing_user.email})
    name_user = await db.execute(
        select(Users).filter(
            Users.name== user.name,
        )
    )
    name_user=name_user.scalars().first()
    if not name_user:
        return generate_error_response(status_code=Exception.UNAUTHORIZED.get("status_code"),message="INCORRECT NAME PROVIDED",error=Exception.UNAUTHORIZED.get("detail"))
        # raise HTTPException(status_code=Exception.UNAUTHORIZED.status_code,detail=str("INCORRECT NAME PROVIDED"))
    data={"access_token":access_token,"token_type":"bearer"}
    return generate_success_response(status_code=200,message=f"{name_user.name} logged in Successfully",data=data)

def send_email(email: str,db:AsyncSession):
    api_key = credentials.get("MAILJET_API")
    api_secret = credentials.get("MAILJET_SECRET_KEY")

    otp = randint(100000, 999999)

    mailjet = Client(auth=(api_key, api_secret), version='v3.1')

    data = {
      'Messages': [
        {
          'From': {
            'Email': credentials.get("EMAIL_ID"),
            'Name': "SENDER"
          },
          'To': [
            {
              'Email': email
            }
          ],
          'Subject': 'Your OTP Verification Code',
          'TextPart': f'Your OTP is {otp}. It will expire in 10 minutes.'
        }
      ]
    }
    print(data)
    try:
        print("Mailjet",mailjet)
        result = mailjet.send.create(data=data)
        print("RESULT",result)
        print(f"OTP sent successfully to {email}")
    except Exception as e:
        print(f"Error sending email: {e}")


async def forget_password(email:str,db:AsyncSession):
    existing_user=await db.execute(select(Users).filter(email==Users.email))
    existing_user=existing_user.scalars().first()
    if not existing_user:
        return generate_error_response(status_code=Exception.NOT_FOUND.get("status_code"),message="USER DOES NOT EXIST",error=Exception.NOT_FOUND.get("detail"))
    #Now check if the user is actually a valid person by sending some otp or link to the same email
    otp=random.randint(100000,999999)
    exp=datetime.utcnow()+timedelta(minutes=10)
    send_email(email=email,db=db)

    GEN_OTP=otp
    EXP=exp

    return generate_success_response(status_code=200,message="OTP SENT SUCCESSFULLY")


async def verify_otp(user_otp:int):

    if GEN_OTP==None or EXP==None or user_otp!=GEN_OTP:
        await generate_error_response(status_code=Exception.CONFLICT.get("status_code"),message="INCORRECT OTP PROVIDED",error=Exception.CONFLICT.get("detail"))

    if EXP <= datetime.utcnow():
        return generate_error_response(status_code=Exception.BAD_REQUEST.get("status_code"), message="OTP EXPIRED",error=Exception.BAD_REQUEST.get("detail"))
    return generate_success_response(status_code=200,message="VERIFIED SUCCESSFULLY")

async def update_password(password:str,email:str,db:AsyncSession):
    existing_user=await db.execute(select(Users).filter(email==Users.email))
    user=existing_user.scalars().first()
    user.password=await utils.get_password_hash(password)

    await db.commit()
    generate_success_response(status_code=200,message="PASSWORD UPDATED SUCCESSFULLY")

    