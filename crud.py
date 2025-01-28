from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import *
from schema import *
from models import Product
import models
from utils import Exception
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


# Cart Operations
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

