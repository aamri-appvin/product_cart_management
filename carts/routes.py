import datetime
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import *
from schema import *
from models import Product
import models
from utils import track_user_activity
from utils.Exception import NOT_FOUND
from auth import utils
from utils.Response import generate_success_response,generate_error_response
from utils import Exception
#  Cart Operations
from fastapi import HTTPException
from utils import global_vars
from fastapi import HTTPException
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

def get_logged_in_user():
    print(f"User logged in: {global_vars.USER_LOGGED_IN}")
    return global_vars.USER_LOGGED_IN 

async def add_product_to_cart(cart_id: int, product_id: int, quantity: int, db: AsyncSession):
    try:
        product_query = await db.execute(select(Product).filter(Product.product_id == product_id))
        product_entry = product_query.scalars().first()
        created_at = updated_at = datetime.utcnow()

        if not product_entry:
            return generate_error_response(
                status_code=Exception.NOT_FOUND.get("status_code"),
                message="PRODUCT NOT AVAILABLE",
                error=Exception.NOT_FOUND.get("detail")
            )

        check_deleted = await db.execute(
            select(Deleted_Products).filter(Deleted_Products.product_id == product_id)
        )
        deleted_entry = check_deleted.scalars().first()

        if deleted_entry:
            return generate_error_response(
                status_code=Exception.NOT_FOUND.get("status_code"),
                message="PRODUCT HAS BEEN DELETED",
                error=Exception.NOT_FOUND.get("detail")
            )

        if product_entry.quantity_in_stock < quantity:
            return generate_error_response(
                status_code=Exception.BAD_REQUEST.get("status_code"),
                message="NOT ENOUGH QUANTITY IN STOCK",
                error=Exception.BAD_REQUEST.get("detail")
            )

        cart_query = await db.execute(
            select(CartItem).filter(CartItem.cart_id == cart_id, CartItem.product_id == product_id)
        )
        existing_cart_item = cart_query.scalars().first()

        if existing_cart_item:
            existing_cart_item.qty += quantity
            existing_cart_item.created_at = created_at
            existing_cart_item.updated_at = updated_at
            db.add(existing_cart_item)
        else:
            new_cart_item = CartItem(cart_id=cart_id, product_id=product_id, qty=quantity)
            new_cart_item.created_at = created_at
            new_cart_item.updated_at = updated_at
            db.add(new_cart_item)

        product_entry.quantity_in_stock -= quantity
        db.add(product_entry)

        await db.commit()

        data = {
            "cart_id": cart_id,
            "product_id": product_id,
            "qty": quantity,
        }
        new_user=User_Info(user_id=get_logged_in_user() , action="added product to cart" , product_id=product_id )
        result=track_user_activity.log_user_activity(new_user)
        print("Activity created")
        return generate_success_response(status_code=200, message="Successfully added to cart", data=data)

    except Exception as e:
        return generate_error_response(
            status_code=Exception.INTERNAL_SERVER_ERROR.get("status_code"),
            message="INTERNAL SERVER ERROR",
            error=str(e)
        )



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
    new_user=User_Info(user_id=get_logged_in_user() , action="created cart")
    result=track_user_activity.log_user_activity(new_user)
    print("Activity created")

    return generate_success_response(status_code=200,message="Successfully created the cart",data=new_cart)


async def get_cart_items(db: AsyncSession, cart_id: int):
    query = await db.execute(select(CartItem).filter(CartItem.cart_id == cart_id))
    data=query.scalars().all()
    cart_items=[
        {
            "cart_item_id":d.cart_item_id,
            "cart_id":d.cart_id,
            "product_id":d.product_id,
            "qty":d.qty,
            "created_at": d.created_at.isoformat() if d.created_at else None,
            "updated_at": d.updated_at.isoformat() if d.updated_at else None
        }
        for d in data
    ]
    new_user=User_Info(user_id=get_logged_in_user() , action=f"get cart items with cart id {cart_id}" )
    result=track_user_activity.log_user_activity(new_user)
    print("Activity created")
    return generate_success_response(status_code=200,count=len(list(cart_items)),message="Successfully rendered all cart items",data=cart_items)


async def remove_item_from_cart(db: AsyncSession, cart_item_id: int, cart_id: int):
    query = await db.execute(
        select(CartItem).filter(
            CartItem.cart_id == cart_id, CartItem.cart_item_id == cart_item_id
        )
    )
    cart_item_entry = query.scalars().first()
    if not cart_item_entry:
        return generate_error_response(status_code=Exception.NOT_FOUND.get("status_code"),
                                        message="ITEM NOT FOUND",
                                        error=Exception.NOT_FOUND.get("detail"))

    product_query = await db.execute(
        select(Product).filter(Product.product_id == cart_item_entry.product_id)
    )
    product_entry = product_query.scalars().first()

    if product_entry:
        product_entry.quantity_in_stock += cart_item_entry.qty
        db.add(product_entry)
    
    cart_item_data = {
        "cart_item_id": cart_item_entry.cart_item_id,
        "cart_id": cart_item_entry.cart_id,
        "product_id": cart_item_entry.product_id,
        "qty": cart_item_entry.qty,
        "created_at": cart_item_entry.created_at.isoformat(),
        "updated_at": cart_item_entry.updated_at.isoformat()
    }
    
    await db.delete(cart_item_entry)
    await db.commit()

    new_user=User_Info(user_id=get_logged_in_user() , action=f"removed item with id {cart_item_entry.cart_item_id} from cart with id {cart_item_entry.cart_id}")
    result=track_user_activity.log_user_activity(new_user)
    print("Activity created")

    return generate_success_response(
        status_code=200, message="Successfully removed item", data=cart_item_data
    )


async def update_cart_item(db: AsyncSession, cart_item_id: int, updated_item: Cart_Item_Update):
    query = await db.execute(select(CartItem).filter(CartItem.cart_item_id == cart_item_id))
    cart_item_entry = query.scalars().first()

    if not cart_item_entry:
        return generate_error_response(status_code=Exception.NOT_FOUND.get("status_code"),
                                        message="PRODUCT NOT FOUND IN CART",
                                        error=Exception.NOT_FOUND.get("detail"))

    product_query = await db.execute(select(Product).filter(Product.product_id == cart_item_entry.product_id))
    product_entry = product_query.scalars().first()

    if not product_entry:
        return generate_error_response(status_code=Exception.NOT_FOUND.get("status_code"),
                                        message=f"Product for cart item ID {cart_item_id} not found",
                                        error=Exception.NOT_FOUND.get("detail"))

    quantity_diff = updated_item.qty - cart_item_entry.qty

    if quantity_diff == 0:
        return cart_item_entry

    if quantity_diff < 0:
        product_entry.quantity_in_stock += abs(quantity_diff)
    elif product_entry.quantity_in_stock >= quantity_diff:
        product_entry.quantity_in_stock -= quantity_diff
    else:
        return generate_error_response(status_code=Exception.CONFLICT.get("status_code"),
                                        message=f"Insufficient stock to update the cart item. Only {product_entry.quantity_in_stock} items available.",
                                        error=Exception.CONFLICT.get("detail"))

    # Update cart item quantity and timestamps
    cart_item_entry.qty = updated_item.qty
    cart_item_entry.updated_at = datetime.utcnow()  # Update the updated_at timestamp

    db.add(cart_item_entry)
    db.add(product_entry)
    await db.commit()

    cart_entry = {
        "cart_item_id": cart_item_entry.cart_item_id,
        "cart_id": cart_item_entry.cart_id,
        "product_id": cart_item_entry.product_id,
        "qty": cart_item_entry.qty,
        "created_at": cart_item_entry.created_at.isoformat(),
        "updated_at": cart_item_entry.updated_at.isoformat()
    }

    new_user=User_Info(user_id=get_logged_in_user() , action=f"updated cart item with id {cart_item_entry.cart_item_id}")
    result=track_user_activity.log_user_activity(new_user)
    print("Activity created")

    return generate_success_response(
        status_code=200, count=1, message="Cart Item Updated Successfully", data=cart_entry
    )
