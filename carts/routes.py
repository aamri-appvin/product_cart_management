from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import *
from schema import *
from models import Product
import models
import Exception
from auth import utils

#  Cart Operations
async def add_product_to_cart(
    cart_id: int, product_id: int, quantity: int, db: AsyncSession
):
    try:
        product_query = await db.execute(
            select(Product).filter(Product.product_id == product_id)
        )
        product_entry = product_query.scalars().first()
        check_deleted=await db.execute(select(Deleted_Products).filter(Deleted_Products.product_id==product_entry.product_id))
        if not product_entry or check_deleted:
            raise HTTPException(
                status_code=Exception.NOT_FOUND.status_code, detail=f"Product with ID {product_id} not found."
            )

        if product_entry.quantity_in_stock < quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock for product ID {product_id}. Available: {product_entry.quantity_in_stock}",
            )
        query = await db.execute(
            select(CartItem).filter(
                CartItem.cart_id == cart_id, CartItem.product_id == product_id
            )
        )
        existing_cart_item = query.scalars().first()

        if existing_cart_item:
            existing_cart_item.qty += quantity
            db.add(existing_cart_item)
        else:
            new_cart_item = CartItem(
                cart_id=cart_id, product_id=product_id, qty=quantity
            )
            db.add(new_cart_item)
        product_entry.quantity_in_stock -= quantity
        db.add(product_entry)  
        await db.commit()
        return existing_cart_item if existing_cart_item else new_cart_item

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

async def create_cart(db:AsyncSession,cart:Create_Cart):
    cart_entry = models.Cart(
    owner_name=cart.owner_name,
)
    db.add(cart_entry)
    await db.commit()
    await db.refresh(cart_entry)
    return cart_entry

async def get_cart_items(db: AsyncSession, cart_id: int):
    query = await db.execute(select(CartItem).filter(CartItem.cart_id == cart_id))
    return query.scalars().all()

async def remove_item_from_cart(db: AsyncSession, cart_item_id: int, cart_id: int):
    query = await db.execute(
        select(CartItem).filter(
            CartItem.cart_id == cart_id, CartItem.cart_item_id == cart_item_id
        )
    )
    cart_item_entry = query.scalars().first()
    if not cart_item_entry:
        return None
    product_query = await db.execute(
        select(Product).filter(Product.product_id == cart_item_entry.product_id)
    )
    product_entry = product_query.scalars().first()

    if product_entry:
        product_entry.quantity_in_stock += cart_item_entry.qty
        db.add(product_entry) 
    await db.delete(cart_item_entry)
    await db.commit()
    return cart_item_entry



async def update_cart_item(db: AsyncSession, cart_item_id: int, updated_item: Cart_Item_Update):
    query = await db.execute(select(CartItem).filter(CartItem.cart_item_id == cart_item_id))
    cart_item_entry = query.scalars().first()
    if not cart_item_entry:
        raise ValueError(f"Cart item with ID {cart_item_id} not found")

    product_query = await db.execute(select(Product).filter(Product.product_id == cart_item_entry.product_id))
    product_entry = product_query.scalars().first()
    if not product_entry:
        raise ValueError(f"Product for cart item ID {cart_item_id} not found")

    quantity_diff = updated_item.qty - cart_item_entry.qty

    if quantity_diff == 0:
        return cart_item_entry
    if quantity_diff < 0:
        product_entry.quantity_in_stock += abs(quantity_diff)
        cart_item_entry.qty = updated_item.qty
    elif product_entry.quantity_in_stock >= quantity_diff:
        product_entry.quantity_in_stock -= quantity_diff
        cart_item_entry.qty = updated_item.qty
    else:
        raise ValueError(
            f"Insufficient stock to update the cart item. Only {product_entry.quantity_in_stock} items available."
        )
    await db.commit()
    return cart_item_entry
