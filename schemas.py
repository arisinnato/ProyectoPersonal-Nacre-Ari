from pydantic import BaseModel
from datetime import date

class UserBase(BaseModel):
    id: str
    nombre: str
    apellido: str
    correo: str
    tipo_usuario: str
    contrasena: str


class UserCreate(UserBase):
   pass

class UserUpdate(UserBase):
    contrasena: str

class User(UserBase):
    id_usuario: int

    class Config:
        orm_mode = True

#producto
class ProductBase(BaseModel):
    id_artesano: int
    id_tipo: str
    nombre: str
    descripcion: str
    precio: str

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    pass

class Product(ProductBase):
    id_producto: int

    class Config:
        orm_mode = True