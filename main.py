from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

import crud, models, schemas
from db.db_config import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/item/", response_model=schemas.ItemBase)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    print("Item: ", item)
    return crud.create_item(db=db, item=item)

@app.post("/item/", response_model=schemas.ItemBase)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    print("Item: ", item)
    return crud.create_item(db=db, item=item)

@app.get("/items/", response_model=list[schemas.ItemBase])
def read_items(request: Request, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return templates.TemplateResponse(
        request=request, name="items.html", context={"items": items}
    )

@app.get("/item/{item_id}", response_model=schemas.ItemBase)
def create_item(item_id: int, db: Session = Depends(get_db)):
    db_item = crud.get_item(db, item_id=item_id)
    if db_item is None: 
        raise HTTPException(status_code=404, detail="User not found")
    return db_item
