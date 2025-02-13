from typing import Optional
from pydantic import BaseModel

class Create_Product(BaseModel):
    name: str
    description: str
    price: float
    quantity_in_stock: int

    class Config:
        orm_mode = True

# Schema for representing a product, includes product_id
class Product(BaseModel):
    product_id: Optional[int]  
    name: str
    description: str
    price: float
    quantity_in_stock: int

    class Config:
        orm_mode = True
class CartItemResponse(BaseModel):
    cart_id: int
    product_id: int
    qty: int
    created_at: str
    updated_at: str

    class Config:
        orm_mode = True 
        
class Cart_Item(BaseModel):
    product_id: int
    cart_id: int
    cart_item_id: Optional[int] = None
    qty: int

    class Config:
        orm_mode = True

class Cart_Item_Update(BaseModel):
    qty:int
    class Config:
        orm_mode = True

class Create_Cart(BaseModel):
    owner_name:str
    class Config:
        orm_mode = True
        
class Cart(BaseModel):
    cart_id:Optional[int]
    owner_name:str
    class Config:
        orm_mode = True

class User_Model(BaseModel):
    name:str
    email:str
    password:str
    class Config:
        orm_mode=True

class User_Info(BaseModel):
    user_id:int
    action:str
    product_id:Optional[int]=None
    class Config:
        orm_mode:True