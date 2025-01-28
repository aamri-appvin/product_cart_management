from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import *
from schema import *
from models import Product
import models
from utils import Exception
from auth import utils

# Product Operations
async def get_product(db: AsyncSession, product_id: int):
    query = await db.execute(select(Product).filter(Product.product_id == product_id))
    query=query.scalars().first()
    check_deleted=await db.execute(select(Deleted_Products).filter(Deleted_Products.product_id==query.product_id))
    if check_deleted:
        raise HTTPException(status_code=Exception.NOT_FOUND.status_code,detail=Exception.NOT_FOUND.detail)
    return query.scalars().first()

async def get_all_products(db: AsyncSession):
    result = await db.execute(
        select(Product).filter(Product.product_id != Deleted_Products.product_id)
    )
    products = result.scalars().all()
    return products


async def create_product(db: AsyncSession, product: Create_Product):
    product_entry = Product(
    name=product.name,
    description=product.description,
    price=product.price,
    quantity_in_stock=product.quantity_in_stock,
)
    db.add(product_entry)
    await db.commit()
    await db.refresh(product_entry)
    return product_entry

async def update_product(db: AsyncSession, product_id: int, product: Create_Product):
    
    query = await db.execute(select(Product).filter(Product.product_id == product_id,Deleted_Products.product_id !=product_id))
    if not query:
        raise HTTPException(status_code=Exception.NOT_FOUND.status_code,detail=Exception.NOT_FOUND.detail)
    existing_product = query.scalars().first()
    if not existing_product:
        return None

    existing_product.name = product.name
    existing_product.description = product.description
    existing_product.price = product.price
    existing_product.quantity_in_stock = product.quantity_in_stock

    await db.commit()
    return existing_product

async def delete_product(db: AsyncSession, product_id: int):
    query = await db.execute(select(Product).filter(Product.product_id == product_id))
    product_entry = query.scalars().first()
    check_deleted=await db.execute(select(Deleted_Products).filter(Deleted_Products.product_id==product_entry.product_id))

    if check_deleted:
        raise HTTPException(status_code=Exception.NOT_FOUND.status_code,detail="THE PRODUCT HAS ALREADY BEEN DELETED")
    
    if not product_entry:
        return None
    deleted_product=Deleted_Products(
        product_id=product_entry.product_id,
        name=product_entry.name,
        description=product_entry.description,
        price=product_entry.price,
        quantity_in_stock=product_entry.quantity_in_stock,
    )
    db.add(deleted_product)
    await db.commit()
    await db.refresh(deleted_product)
    return deleted_product

