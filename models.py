from sqlalchemy import Integer, String, Float,Numeric
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Column, Integer, String,VARCHAR
class Base(DeclarativeBase):
    pass


class Cart(Base):
    __tablename__ = "carts"
    
    cart_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    owner_name: Mapped[str] = mapped_column(String, nullable=False)


class CartItem(Base):
    __tablename__ = "cart_items"

    cart_item_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    cart_id: Mapped[int] = mapped_column(Integer, nullable=False) 
    product_id: Mapped[int] = mapped_column(Integer, nullable=False)
    qty: Mapped[int] = mapped_column(Integer, nullable=False)


class Product(Base):
    __tablename__ = "products"

    product_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(255))
    price: Mapped[float] = mapped_column(Numeric)
    quantity_in_stock: Mapped[int] = mapped_column(Integer)
    
#Table for testing alembic
class Sample_Table(Base):
   __tablename__='sample_table'

   id:Mapped[int]=mapped_column(Integer,primary_key=True,autoincrement=True)
   name:Mapped[str]=mapped_column(String(50),nullable=False)
   age:Mapped[int]=mapped_column(Integer,nullable=True)

class Deleted_Products(Base):
    __tablename__ = 'deleted_products'
    
    product_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(255))
    price: Mapped[float] = mapped_column(Numeric)
    quantity_in_stock: Mapped[int] = mapped_column(Integer)

class Users(Base):
    __tablename__="users"
    
    id:Mapped[int]=mapped_column(Integer,primary_key=True,index=True)
    name:Mapped[str]=mapped_column(String,nullable=False)
    email:Mapped[str]=mapped_column(String,nullable=False)
    password:Mapped[VARCHAR]=mapped_column(VARCHAR(255))


#Testing Purpose
class Sample_Table2(Base):
    __tablename__ = 'sample_table2'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)

