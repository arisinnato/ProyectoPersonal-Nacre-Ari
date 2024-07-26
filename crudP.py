from sqlalchemy.orm import Session
import models, schemas

def get_producto(db: Session, producto_id: int):
    return db.query(models.Product).filter(models.Product.id == producto_id).first()

def agregar_producto_al_carrito(db: Session, carrito_item: schemas.CarritoCreate):
    db_carrito_item = models.Cart(**carrito_item.dict())
    db.add(db_carrito_item)
    db.commit()
    db.refresh(db_carrito_item)
    return db_carrito_item

def get_productos_del_carrito(db: Session):
    return db.query(models.Carrito).all()