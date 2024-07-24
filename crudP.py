from sqlalchemy.orm import Session
import models, schemas
#
def create_product(db: Session, products: schemas.ProductCreate):
    db_product = models.Product(
        id=products.id,
        nombre=products.nombre,
        descripcion=products.descripcion,
        precio = products.precio
    )

    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product
    



def get_product_by_id(db: Session, product_id: int):
    return db.query(models.Producto).filter(models.Producto.id_producto == product_id).first()

def update_product(db: Session, product_id: int, product: schemas.ProductUpdate):
    db_product = get_product_by_id(db, product_id)
    if db_product is None:
        return None
    for key, value in product.dict().items():
        if value:
            setattr(db_product, key, value)
    db.commit()
    db.refresh(db_product)
    return db_product

def delete_product(db: Session, product_id: int):
    db_product = get_product_by_id(db, product_id)
    if db_product is None:
        return None
    db.delete(db_product)
    db.commit()
    return db_product


def get_products(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Producto).offset(skip).limit(limit).all()

'''def get_types(db: Session, skip: int = 10, limit: int = 100):
    return db.query(models.Tipo_Producto).offset(skip).limit(limit).all()'''