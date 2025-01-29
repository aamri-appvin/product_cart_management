from decimal import Decimal
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

# Product Operations
async def get_product(db: AsyncSession, product_id: int):
    query = await db.execute(select(Product).filter(Product.product_id == product_id))
    product = query.scalars().first()
    if not product:
        return generate_error_response(status_code=Exception.NOT_FOUND.get("status_code"),message="PRODUCT NOT AVAILABLE",error=Exception.NOT_FOUND.get("detail"))
        # raise HTTPException(status_code=Exception.NOT_FOUND.get("status_code"), detail=Exception.NOT_FOUND.get("detail"))
    check_deleted = await db.execute(select(Deleted_Products).filter(Deleted_Products.product_id == product.product_id))
    deleted_product = check_deleted.scalars().first()

    if deleted_product:
        return generate_error_response(status_code=Exception.NOT_FOUND.get("status_code"),message="PRODUCT HAS BEEN DELETED",error=Exception.NOT_FOUND.get("detail"))
        # raise HTTPException(status_code=Exception.NOT_FOUND.get("status_code"), detail=Exception.NOT_FOUND.get("detail"))
    new_product={
        "product_id": product.product_id,
        "name": product.name,
        "description": product.description,
        "price": float(product.price) if isinstance(product.price,Decimal) else product.price,
        "quantity_in_stock": product.quantity_in_stock
    }
    return generate_success_response(status_code=200,message="Success",data=new_product)


async def get_all_products(db: AsyncSession):
    result = await db.execute(
        select(Product).filter(Product.product_id != Deleted_Products.product_id)
    )
    products = result.scalars().all()
    new_product=[
    {
        "product_id": p.product_id,
        "name": p.name,
        "description": p.description,
        "price": float(p.price) if isinstance(p.price, Decimal) else p.price,
        "quantity_in_stock": p.quantity_in_stock
    }
    for p in products]
    return generate_success_response(status_code=200, message="Successful", data=new_product)


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
    new_product={
        "product_id": product_entry.product_id,
        "name": product_entry.name,
        "description": product_entry.description,
        "price": float(product_entry.price) if isinstance(product_entry.price,Decimal) else product_entry.price,
        "quantity_in_stock": product_entry.quantity_in_stock
    }
    return generate_success_response(status_code=200,message="Successful",data=new_product)

async def update_product(db: AsyncSession, product_id: int, product: Create_Product):
    
    query = await db.execute(select(Product).filter(Product.product_id == product_id,Deleted_Products.product_id !=product_id))
    if not query:
        return generate_error_response(status_code=Exception.NOT_FOUND.get("status_code"),message="PRODUCT NOT AVAILABLE",error=Exception.NOT_FOUND.get("detail"))
        # raise HTTPException(status_code=Exception.NOT_FOUND.get("status_code"),detail=Exception.NOT_FOUND.get("detail"))
    existing_product = query.scalars().first()
    if not existing_product:
        return None

    existing_product.name = product.name
    existing_product.description = product.description
    existing_product.price = product.price
    existing_product.quantity_in_stock = product.quantity_in_stock
    new_product={
        "product_id": existing_product.product_id,
        "name": existing_product.name,
        "description": existing_product.description,
        "price":float(existing_product.price) if isinstance(existing_product.price,Decimal) else existing_product.price, 
        "quantity_in_stock": existing_product.quantity_in_stock
    }
    await db.commit()
    return generate_success_response(status_code=200,message="Success",data=new_product)

async def delete_product(db: AsyncSession, product_id: int):
    query = await db.execute(select(Product).filter(Product.product_id == product_id,Deleted_Products.product_id!=product_id))
    product_entry = query.scalars().first()
    
    if not product_entry:
        return generate_error_response(status_code=Exception.NOT_FOUND.get("status_code"),message="PRODUCT NOT AVAILABLE OR HAS BEEN REMOVED",error=Exception.NOT_FOUND.get("detail"))
        # raise HTTPException(status_code=Exception.NOT_FOUND.get("status_code"),detail=Exception.NOT_FOUND.get("detail"))
    deleted_product=Deleted_Products(
        product_id=product_entry.product_id,
        name=product_entry.name,
        description=product_entry.description,
        price=product_entry.price,
        quantity_in_stock=product_entry.quantity_in_stock,
    )
    db.add(deleted_product)
    new_product={
        "product_id": product_entry.product_id,
        "name": product_entry.name,
        "description": product_entry.description,
        "price": float(product_entry.price) if isinstance(product_entry.price,Decimal) else product_entry.price,
        "quantity_in_stock": product_entry.quantity_in_stock
    }
    await db.commit()
    await db.refresh(deleted_product)
    return generate_success_response(status_code=200,message="Success",data=new_product)

