from fastapi import Depends, FastAPI, HTTPException, Request, Form, status, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from datetime import timedelta

import models, schemas, crud, crudP, auth
from db.db_config import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(middleware=[
    Middleware(SessionMiddleware, secret_key="your_secret_key")
])

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")



ACCESS_TOKEN_EXPIRE_MINUTES = 30

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/register", response_class=HTMLResponse)
async def register_user(request: Request, 
                        username: str = Form(...), 
                        email: str = Form(...), 
                        password: str = Form(...), 
                        full_name: str = Form(...), 
                        date_of_birth: str = Form(...), 
                        db: Session = Depends(get_db)):
    user = schemas.UserCreate(username=username, 
                              email=email, 
                              password=password, 
                              full_name=full_name, 
                              date_of_birth=date_of_birth)
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    crud.create_user(db=db, user=user)
    return templates.TemplateResponse("register.html", {"request": request, "message": "User registered successfully!"})

@app.get("/register", response_class=HTMLResponse)
async def register_user_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/token", response_class=HTMLResponse)
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, username=form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response

@app.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/logout", response_class=HTMLResponse)
async def logout(request: Request):
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("access_token")
    return response

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/products", response_class=HTMLResponse)
async def read_products(request: Request, db: Session = Depends(get_db)):
    products = crudP.get_products(db)
    return templates.TemplateResponse("products.html", {"request": request, "products": products})

@app.post("/add_to_cart", response_class=HTMLResponse)
async def add_to_cart(request: Request, product_id: int = Form(...), db: Session = Depends(get_db)):
    user_token = request.cookies.get("access_token")
    if not user_token:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    
    user_token = user_token.split("Bearer ")[1]
    username = auth.decode_access_token(user_token)
    if not username:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    user = crud.get_user_by_username(db, username)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    product = crudP.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    crudP.add_to_cart(db, user_id=user.id, product_id=product.id)
    return RedirectResponse(url="/products", status_code=status.HTTP_302_FOUND)

@app.get("/cart", response_class=HTMLResponse)
async def view_cart(request: Request, db: Session = Depends(get_db)):
    user_token = request.cookies.get("access_token")
    if not user_token:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    
    user_token = user_token.split("Bearer ")[1]
    username = auth.decode_access_token(user_token)
    if not username:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    user = crud.get_user_by_username(db, username)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    cart_items = crudP.get_cart_items(db, user_id=user.id)
    return templates.TemplateResponse("cart.html", {"request": request, "cart_items": cart_items})
