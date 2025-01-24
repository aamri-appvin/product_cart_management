from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import *
from schema import *
from models import Product
import models
# Product Operations
async def get_product(db: AsyncSession, product_id: int):
    query = await db.execute(select(Product).filter(Product.product_id == product_id))
    print(query)
    return query.scalars().first()


async def get_all_products(db: AsyncSession):
    query = await db.execute(select(Product))
    return query.scalars().all()


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
    query = await db.execute(select(Product).filter(Product.product_id == product_id))
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
    if not product_entry:
        return None

    await db.delete(product_entry)
    await db.commit()
    return product_entry


# Cart Operations
async def add_product_to_cart(db: AsyncSession, cart_id: int, product_id: int, quantity: int):
    query = await db.execute(select(Product).filter(Product.product_id == product_id))
    product_entry = query.scalars().first()
    if not product_entry:
        raise ValueError("Product not found")

    if product_entry.quantity_in_stock < quantity:
        raise ValueError("Insufficient stock for this product")

    product_entry.quantity_in_stock -= quantity
    db_cart_item = CartItem(cart_id=cart_id, product_id=product_id, qty=quantity)


    db.add_all([product_entry, db_cart_item])
    await db.commit()
    await db.refresh(db_cart_item)
    return db_cart_item

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


async def remove_item_from_cart(db: AsyncSession, cart_item_id: int):
    query = await db.execute(select(CartItem).filter(CartItem.cart_item_id == cart_item_id))
    cart_item_entry = query.scalars().first()
    if not cart_item_entry:
        return None

    product_query = await db.execute(select(Product).filter(Product.product_id == cart_item_entry.product_id))
    product_entry = product_query.scalars().first()
    if product_entry:
        product_entry.quantity_in_stock += cart_item_entry.qty

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

