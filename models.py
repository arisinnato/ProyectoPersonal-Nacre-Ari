from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from db.db_config import Base

class Item(Base):
    __tablename__  = "items"
    
    id = Column(Integer, primary_key=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    category = Column(String, index=True)
    type = Column(String, index=True)

class Usuario(Base): 
    __tablename__  = "usuarios"
    
    id = Column(String, primary_key=True, index=True)
    nombres = Column(String, index=True)
    apellidos = Column(String, index=True)
    correo = Column(String, index=True)
    contraseña = Column(String, index=True)

class Tipo_Usuario(Base): 
    __tablename__  = "tipos_usuarios"
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String, index=True)
    descripcion = Column(String, index=True)

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String)
    price = Column(Float, nullable=False)
    image = Column(String)
    categoria = Column(String)

class Like(Base):
    __tablename__ = 'likes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)

class Purchase(Base):
    __tablename__ = 'purchases'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    date = Column(DateTime, nullable=False)
    total = Column(Float, nullable=False)

class PurchaseDetail(Base):
    __tablename__ = 'purchase_details'
    id = Column(Integer, primary_key=True, autoincrement=True)
    purchase_id = Column(Integer, ForeignKey('purchases.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)


    purchase = relationship('Purchase', back_populates='purchase_details')
    product = relationship('Product', back_populates='purchase_details')

class Carrito(Base):
    __tablename__ = "carrito"

    id = Column(Integer, primary_key=True, index=True)
    producto_id = Column(Integer, ForeignKey("products.id"))
    cantidad = Column(Integer, default=1)

    producto = relationship("Product")