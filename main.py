import json
from fastapi import FastAPI, APIRouter, Depends, HTTPException, status , UploadFile
from fastapi.responses import StreamingResponse
from minio import S3Error
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
# from utils.Get_User import authenticate_user
from utils.Response import generate_error_response
import auth.routes
from auth.routes import verify_otp
import carts.routes
from database import engine, Base, get_db
import products.routes
import schema
import crud
from models import Product, CartItem, Cart
import auth
import products
import carts
from utils.Exception import CONFLICT,BAD_REQUEST, NOT_FOUND,UNAUTHORIZED
from utils.Get_User import secure_endpoint
from minio_client import minio_client
import os 
import io
from clickhouse_driver import Client
from utils import track_user_activity
import version
from version import update_version


clickhouse_driver=Client(host='localhost',port='9000')
app = FastAPI()
bucket_name="samplebucket"

if not minio_client.bucket_exists(bucket_name):
    minio_client.make_bucket(bucket_name)



#Version router
version_router=APIRouter(prefix="/version",tags=["Version"])

@app.get("/version_info")
def get_version_info():
    return version.get_version()

@app.post("/update_version")
def update_versionn(component:str,version:str):
    return update_version(component,version)

#Auth router
auth_router = APIRouter(prefix="/auth", tags=["Auth"])

@app.post("/signup/")
async def user_signup(user:schema.User_Model,db:AsyncSession=Depends(get_db)):
    print("Calling user signup")
    return await auth.routes.user_signup(user,db)


@app.post("/login")
async def user_login(user:schema.User_Model,db:AsyncSession=Depends(get_db)):
    return await auth.routes.user_login(user,db)

@app.post("/forget_password")
async def forget_password(email:str,db:AsyncSession=Depends(get_db)):
    return await auth.routes.forget_password(email,db)

@app.post("/verify_otp")
async def verify_user_otp(user_otp:int,updated_password:str , db:AsyncSession=Depends(get_db) ):
    response=await verify_otp(user_otp)
    print("RESPONse",response)
    if response.status_code==200:
        return await auth.routes.update_password(updated_password,db)
    else:
        return generate_error_response(status_code=UNAUTHORIZED.get("status_code"),message="INCORRECT OTP PROVIDED",error=UNAUTHORIZED.get("detail"))
    
# Products Router
products_router = APIRouter(prefix="/products", tags=["Products"])

@products_router.post("/", response_model=schema.Product)
async def create_product(
    product: schema.Create_Product, db: AsyncSession = Depends(get_db) , current_user:str=Depends(secure_endpoint)
):
    print("Product Creation Initiated")
    print("Current User",current_user)
    return await products.routes.create_product(db=db,product=product)


@products_router.get("/", response_model=List[schema.Product])
async def get_product(product_id: Optional[int] = None, db: AsyncSession = Depends(get_db), current_user:str=Depends(secure_endpoint)):
    if product_id is None:
        return await products.routes.get_all_products(db=db)
    else:

        db_product = await products.routes.get_product(db=db, product_id=product_id)
        print("your product",db_product)
        if db_product is None:
            raise HTTPException(status_code=404, detail="PRODUCT NOT FOUND!")
        return db_product

@products_router.put("/{product_id}", response_model=schema.Product)
async def update_product(
    product_id: int, product: schema.Create_Product, db: AsyncSession = Depends(get_db),current_user:str=Depends(secure_endpoint)
):
    updated=await products.routes.update_product(db=db,product_id=product_id,product=product)
    if updated is None:
        raise HTTPException(status_code=NOT_FOUND.get("status_code"), detail=NOT_FOUND.get("detail"))
    return updated
@products_router.delete('/{product_id}',response_model=schema.Product)
async def delete_product(product_id: int,db: AsyncSession = Depends(get_db) , current_user:str=Depends(secure_endpoint)):
    deleted=await products.routes.delete_product(db=db,product_id=product_id)
    return deleted



# Cart Router
cart_router = APIRouter(prefix="/cart", tags=["Cart"])

@cart_router.post("/create")
async def create_cart(cart:schema.Create_Cart,db:AsyncSession=Depends(get_db),current_user:str=Depends(secure_endpoint)):
    return await carts.routes.create_cart(db,cart)

@cart_router.post("/add", response_model=schema.Cart_Item)
async def add_product_to_cart(
    cart_id: int, product_id: int, quantity: int, db: AsyncSession = Depends(get_db),current_user:str=Depends(secure_endpoint)
):
    try:
        return await carts.routes.add_product_to_cart(
            db=db, cart_id=cart_id, product_id=product_id, quantity=quantity
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@cart_router.get("/items/{cart_id}")
async def get_cart_items(cart_id: int, db: AsyncSession = Depends(get_db),current_user:str=Depends(secure_endpoint)):
    return await carts.routes.get_cart_items(db=db,cart_id=cart_id)

@cart_router.delete("/remove/{cart_item_id}/{cart_id}")
async def remove_item_from_cart(cart_item_id: int,cart_id:int, db: AsyncSession = Depends(get_db),current_user:str=Depends(secure_endpoint)):
    cart_item = await carts.routes.remove_item_from_cart(db=db, cart_item_id=cart_item_id,cart_id=cart_id)
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="CART ITEM NOT FOUND"
        )
    return cart_item

@cart_router.put("/update/{cart_item_id}", response_model=schema.Cart_Item)
async def update_cart_item(
    cart_item_id: int,
    cart_item: schema.Cart_Item_Update,
    db: AsyncSession = Depends(get_db),
    current_user:str=Depends(secure_endpoint)
):
    try:
        return await carts.routes.update_cart_item(
            db=db, cart_item_id=cart_item_id, updated_item=cart_item
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))



@app.post("/upload")
async def file_upload(file: UploadFile):
    try:
        file_content=await file.read()

        file_size=len(file_content)   

        file_stream=io.BytesIO(file_content)

        minio_client.put_object(
        bucket_name=bucket_name,
        object_name=file.filename,
        data=file_stream,
        length=file_size,
        content_type=file.content_type
        )
        # os.remove(file_path)
        return {"message":f"File {file.filename} has successfully uploaded."}
    except S3Error as e:
        raise HTTPException(status_code=500,detail=str(e))
    
@app.get("/download/{filename}")
def download_file(filename:str):
    try:
        file_data=minio_client.get_object(bucket_name,filename)
        return StreamingResponse(file_data,media_type="application/octet-stream")
    except S3Error as e:
        raise HTTPException(status_code=500,detail=str(e))

@app.get("/get_objects/{bucket_name}")
def get_objects(bucket_name:str):
    data=minio_client.list_objects(bucket_name)
    print(data)
    return {"data":data}

@app.delete("/delete_file/{bucket_name}/{filename}")
def delete_objects(bucket_name:str,filename:str):
    obj=minio_client.get_object(bucket_name,filename)
    print(obj,"is the deleted object")
    minio_client._delete_objects(bucket_name,filename)
    return obj


#User Activity tracking
user_router=APIRouter(prefix='/user',tags=['User'])

@user_router.post('/track_user_action')
def track(user:schema.User_Info):
    result=track_user_activity.log_user_activity(user)
    print("Activity created")
    return result




app.include_router(auth_router)
app.include_router(products_router)
app.include_router(cart_router)
app.include_router(user_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
