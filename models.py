from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float

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
