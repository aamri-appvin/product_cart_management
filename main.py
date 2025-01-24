from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from database import engine, Base, get_db
import schema
import crud
from models import Product, CartItem, Cart

# Initialize the FastAPI application
app = FastAPI()

# # Create database tables asynchronously
# @app.on_event("startup")
# async def init_db():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)

# Products Router
products_router = APIRouter(prefix="/products", tags=["Products"])

@products_router.post("/", response_model=schema.Product)
async def create_product(
    product: schema.Create_Product, db: AsyncSession = Depends(get_db)
):
    return await crud.create_product(db=db, product=product)

@products_router.get("/", response_model=List[schema.Product])
async def get_all_products(db: AsyncSession = Depends(get_db)):
    return await crud.get_all_products(db=db)

@products_router.get("/{product_id}", response_model=schema.Product)
async def get_product_by_id(product_id: int, db: AsyncSession = Depends(get_db)):
    db_product = await crud.get_product(db=db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

@products_router.put("/{product_id}", response_model=schema.Product)
async def update_product(
    product_id: int, product: schema.Create_Product, db: AsyncSession = Depends(get_db)
):
    updated = await crud.update_product(db=db, product_id=product_id, product=product)
    if updated is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated

# Cart Router
cart_router = APIRouter(prefix="/cart", tags=["Cart"])

@cart_router.post("/create")
async def create_cart(cart:schema.Create_Cart,db:AsyncSession=Depends(get_db)):
    return await crud.create_cart(db,cart)

@cart_router.post("/add", response_model=schema.Cart_Item)
async def add_product_to_cart(
    cart_id: int, product_id: int, quantity: int, db: AsyncSession = Depends(get_db)
):
    try:
        return await crud.add_product_to_cart(
            db=db, cart_id=cart_id, product_id=product_id, quantity=quantity
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@cart_router.get("/{cart_id}/items")
async def get_cart_items(cart_id: int, db: AsyncSession = Depends(get_db)):
    return await crud.get_cart_items(db=db, cart_id=cart_id)

@cart_router.delete("/remove/{cart_item_id}")
async def remove_item_from_cart(cart_item_id: int, db: AsyncSession = Depends(get_db)):
    cart_item = await crud.remove_item_from_cart(db=db, cart_item_id=cart_item_id)
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found"
        )
    return cart_item

@cart_router.put("/update/{cart_item_id}", response_model=schema.Cart_Item)
async def update_cart_item(
    cart_item_id: int,
    cart_item: schema.Cart_Item_Update,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await crud.update_cart_item(
            db=db, cart_item_id=cart_item_id, updated_item=cart_item
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# Register routers
app.include_router(products_router)
app.include_router(cart_router)

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
