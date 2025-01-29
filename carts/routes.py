from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import *
from schema import *
from models import Product
import models
from utils.Exception import NOT_FOUND
from auth import utils
from utils.Response import generate_success_response,generate_error_response
from utils import Exception
#  Cart Operations
from fastapi import HTTPException

async def add_product_to_cart(cart_id: int, product_id: int, quantity: int, db: AsyncSession):
    try:
        product_query = await db.execute(select(Product).filter(Product.product_id == product_id))
        product_entry = product_query.scalars().first()

        if not product_entry:
            return generate_error_response(status_code=Exception.NOT_FOUND.get("status_code"),message="PRODUCT NOT AVAILABLE",error=Exception.NOT_FOUND.get("detail"))
            # raise HTTPException(status_code=NOT_FOUND.get("status_code"), detail=NOT_FOUND.get("detail"))

        check_deleted = await db.execute(
            select(Deleted_Products).filter(Deleted_Products.product_id == product_id)
        )
        deleted_entry = check_deleted.scalars().first()
        
        if deleted_entry:
            return generate_error_response(status_code=Exception.NOT_FOUND.get("status_code"),message="PRODUCT HAS BEEN DELETED",error=Exception.NOT_FOUND.get("detail"))
            # raise HTTPException(status_code=NOT_FOUND.get("status_code"), detail=NOT_FOUND.get("detail"))

        if product_entry.quantity_in_stock < quantity:
            return generate_error_response(status_code=Exception.BAD_REQUEST.get("status_code"),message="NOT ENOUGH QUANTITY IN STOCK",error=Exception.BAD_REQUEST.get("detail"))
            # raise HTTPException(
            #     status_code=400,
            #     detail=f"Not enough stock for product ID {product_id}. Available: {product_entry.quantity_in_stock}",
            # )

        cart_query = await db.execute(
            select(CartItem).filter(CartItem.cart_id == cart_id, CartItem.product_id == product_id)
        )
        existing_cart_item = cart_query.scalars().first()

        if existing_cart_item:
            existing_cart_item.qty += quantity
            db.add(existing_cart_item)
        else:
            new_cart_item = CartItem(cart_id=cart_id, product_id=product_id, qty=quantity)
            db.add(new_cart_item)

        product_entry.quantity_in_stock -= quantity
        db.add(product_entry)

        await db.commit()
        data= Cart_Item(
            cart_id=cart_id,
            product_id=product_id,
            qty=quantity,
        )
        return generate_success_response(status_code=200,message="Success",data=data)

    except Exception as e:
        return generate_error_response(status_code=Exception.INTERNAL_SERVER_ERROR.get("INTERNAL SERVER ERROR",error=Exception.INTERNAL_SERVER_ERROR.get("detail")))


async def create_cart(db:AsyncSession,cart:Create_Cart):
    cart_entry = models.Cart(
    owner_name=cart.owner_name,
)
    db.add(cart_entry)
    await db.commit()
    await db.refresh(cart_entry)
    new_cart={
       "cart_id":cart_entry.cart_id,
       "owner_name":cart_entry.owner_name
    }
    return generate_success_response(status_code=200,message="Success",data=new_cart)

async def get_cart_items(db: AsyncSession, cart_id: int):
    query = await db.execute(select(CartItem).filter(CartItem.cart_id == cart_id))
    data=query.scalars().all()
    cart_items=[
        {
            "cart_item_id":d.cart_item_id,
            "cart_id":d.cart_id,
            "product_id":d.product_id,
            "qty":d.qty,
        }
        for d in data
    ]
    return generate_success_response(status_code=200,message="Success",data=cart_items)

async def remove_item_from_cart(db: AsyncSession, cart_item_id: int, cart_id: int):
    query = await db.execute(
        select(CartItem).filter(
            CartItem.cart_id == cart_id, CartItem.cart_item_id == cart_item_id
        )
    )
    cart_item_entry = query.scalars().first()
    if not cart_item_entry:
        return generate_error_response(status_code=Exception.NOT_FOUND.get("status_code"),message="ITEM NOT FOUND",error=Exception.NOT_FOUND.get("detail"))
    product_query = await db.execute(
        select(Product).filter(Product.product_id == cart_item_entry.product_id)
    )
    product_entry = product_query.scalars().first()

    if product_entry:
        product_entry.quantity_in_stock += cart_item_entry.qty
        db.add(product_entry) 
    await db.delete(cart_item_entry)
    await db.commit()
    cart_item={
            "cart_item_id":cart_item_entry.cart_item_id,
            "cart_id":cart_item_entry.cart_id,
            "product_id":cart_item_entry.product_id,
            "qty":cart_item_entry.qty
        }
    return generate_success_response(status_code=200,message="Success",data=cart_item)



async def update_cart_item(db: AsyncSession, cart_item_id: int, updated_item: Cart_Item_Update):
    query = await db.execute(select(CartItem).filter(CartItem.cart_item_id == cart_item_id))
    cart_item_entry = query.scalars().first()
    if not cart_item_entry:
        return generate_error_response(status_code=Exception.NOT_FOUND.get("status_code"),message="PRODUCT NOT FOUND IN CART",error=Exception.NOT_FOUND.get("detail"))
        # raise ValueError(f"Cart item with ID {cart_item_id} not found")

    product_query = await db.execute(select(Product).filter(Product.product_id == cart_item_entry.product_id))
    product_entry = product_query.scalars().first()
    if not product_entry:
        return generate_error_response(status_code=Exception.NOT_FOUND.get("status_code"),message=f"Product for cart item ID {cart_item_id} not found",error=Exception.NOT_FOUND.get("detail"))
        # raise ValueError(f"Product for cart item ID {cart_item_id} not found")

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
        return generate_error_response(status_code=Exception.CONFLICT.get("status_code"),message=f"Insufficient stock to update the cart item. Only {product_entry.quantity_in_stock} items available.",error=Exception.CONFLICT.get("detail"))
        # raise ValueError(
            # f"Insufficient stock to update the cart item. Only {product_entry.quantity_in_stock} items available."
        # )
    await db.commit()
    cart_entry={
            "cart_item_id":cart_item_entry.cart_item_id,
            "cart_id":cart_item_entry.cart_id,
            "product_id":cart_item_entry.product_id,
            "qty":cart_item_entry.qty
        }
    return generate_success_response(status_code=200,message="Success",data=cart_entry)
    # return cart_item_entry
