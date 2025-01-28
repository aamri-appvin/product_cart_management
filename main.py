from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import auth.routes
import carts.routes
from database import engine, Base, get_db
import products.routes
import schema
import crud
from models import Product, CartItem, Cart
import Exception
import auth
import products
import carts
app = FastAPI()


#Auth router
auth_router = APIRouter(prefix="/auth", tags=["Auth"])

@app.post("/signup/")
async def user_signup(user:schema.User_Model,db:AsyncSession=Depends(get_db)):
    print("Calling user signup")
    return await auth.routes.user_signup(user,db)


@app.post("/login")
async def user_login(user:schema.User_Model,db:AsyncSession=Depends(get_db)):
    return await auth.routes.user_login(user,db)

# Products Router
products_router = APIRouter(prefix="/products", tags=["Products"])

@products_router.post("/", response_model=schema.Product)
async def create_product(
    product: schema.Create_Product, db: AsyncSession = Depends(get_db)
):
    return await products.routes.create_product(db=db,product=product)

@products_router.get("/", response_model=List[schema.Product])
async def get_all_products(db: AsyncSession = Depends(get_db)):
    return await products.routes.get_all_products(db=db)

@products_router.get("/{product_id}", response_model=schema.Product)
async def get_product_by_id(product_id: int, db: AsyncSession = Depends(get_db)):
    db_product=await products.routes.get_product(db=db,product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=Exception.NOT_FOUND.status_code, detail="PRODUCT NOT FOUND!")
    return db_product

@products_router.put("/{product_id}", response_model=schema.Product)
async def update_product(
    product_id: int, product: schema.Create_Product, db: AsyncSession = Depends(get_db)
):
    updated=await products.routes.update_product(db=db,product_id=product_id,product=product)
    if updated is None:
        raise HTTPException(status_code=Exception.NOT_FOUND.status_code, detail="PRODUCT NOT FOUND")
    return updated
@products_router.delete('/{product_id}',response_model=schema.Product)
async def delete_product(product_id: int,db: AsyncSession = Depends(get_db)):
    deleted=await products.routes.delete_product(db=db,product_id=product_id)
    return deleted





# Cart Router
cart_router = APIRouter(prefix="/cart", tags=["Cart"])

@cart_router.post("/create")
async def create_cart(cart:schema.Create_Cart,db:AsyncSession=Depends(get_db)):
    return await carts.routes.create_cart(db,cart)

@cart_router.post("/add", response_model=schema.Cart_Item)
async def add_product_to_cart(
    cart_id: int, product_id: int, quantity: int, db: AsyncSession = Depends(get_db)
):
    try:
        return await carts.routes.add_product_to_cart(
            db=db, cart_id=cart_id, product_id=product_id, quantity=quantity
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@cart_router.get("/items/{cart_id}")
async def get_cart_items(cart_id: int, db: AsyncSession = Depends(get_db)):
    return await carts.routes.get_cart_items(db=db,cart_id=cart_id)

@cart_router.delete("/remove/{cart_item_id}/{cart_id}")
async def remove_item_from_cart(cart_item_id: int,cart_id:int, db: AsyncSession = Depends(get_db)):
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
):
    try:
        return await carts.routes.update_cart_item(
            db=db, cart_item_id=cart_item_id, updated_item=cart_item
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

app.include_router(auth_router)
app.include_router(products_router)
app.include_router(cart_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
