from fastapi import Depends, FastAPI, HTTPException, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from fastapi.middleware import Middleware
from sqlalchemy import Double
from starlette.middleware.sessions import SessionMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordRequestForm, OAuth2PasswordBearer
import models, schemas, crud, crudP
from db.db_config import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# Inicializar la aplicación FastAPI con el middleware de sesión
app = FastAPI(middleware=[
    Middleware(SessionMiddleware, secret_key="your_secret_key")
])

# Montar el directorio estático para servir archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Configurar Jinja2 para la renderización de plantillas
templates = Jinja2Templates(directory="templates")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="iniciar_sesion_post")

# Dependencia para obtener la sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/user/create/", response_model=schemas.UserBase)
async def create_usuario_post(request: Request, 
                        id: str = Form(...), 
                        nombre: str = Form(...), 
                        apellido: str = Form(...), 
                        correo_electronico: str = Form(...), 
                        contrasena: str = Form(...), 
                        tipo_usuario : str = Form(...),
                        db: Session = Depends(get_db)):
    print("Usuario: ", correo_electronico)
    user = schemas.UserCreate(id=id, 
                              nombre=nombre, 
                              apellido=apellido, 
                              correo_electronico=correo_electronico, 
                              contrasena=contrasena, 
                              tipo_usuario=tipo_usuario)
    db_user = crud.get_user_by_email(db, email=user.correo_electronico)
    print("Db user: ", db_user)
    if db_user: 
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = crud.get_user_by_ci(db, user_id=user.id)
    if db_user: 
        raise HTTPException(status_code=400, detail="CI already registered")
    crud.create_user(db=db, user=user)
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/usuario/create/", response_class=HTMLResponse)
async def create_usuario_template(request: Request):
    print("Usuario get: ", )
    return templates.TemplateResponse("registro.html", {"request": request})




@app.get("/user/{user_id}", response_class=HTMLResponse)
async def read_usuario(request: Request, item_id: int, db: Session = Depends(get_db)):
    item = crud.get_user_by_ci(db, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="User not found")
    return templates.TemplateResponse("profile.html", {"request": request, "item": item})


#Excepciones
#@app.exception_handler(Requires_el_Login_de_Exception)
#async def exception_handler(request: Request, exc: Requires_el_Login_de_Exception) -> Response:
#    return templates.TemplateResponse("message-redirection.html", {"request": request, "message": exc.message, "path_route": exc.path_route, "path_message": exc.path_message})

'''@app.exception_handler(LoginExpired)
async def exception_handler(request: Request, exc: Requires_el_Login_de_Exception) -> Response:
    return templates.TemplateResponse("message-redirection.html", {"request": request, "message": exc.message, "path_route": exc.path_route, "path_message": exc.path_message})

@app.exception_handler(Exception_No_Apto_Para_Artesano)
async def exception_handler(request: Request, exc: Requires_el_Login_de_Exception) -> Response:
    return templates.TemplateResponse("message-redirection.html", {"request": request, "message": exc.message, "path_route": exc.path_route, "path_message": exc.path_message})

@app.exception_handler(Exception_No_Apto_Para_Cliente)
async def exception_handler(request: Request, exc: Requires_el_Login_de_Exception) -> Response:
    return templates.TemplateResponse("message-redirection.html", {"request": request, "message": exc.message, "path_route": exc.path_route, "path_message": exc.path_message})'''



# Iniciar sesión
@app.get("/iniciarsesion/", response_class=HTMLResponse)
async def iniciar_sesion_template(request: Request):
    return templates.TemplateResponse("iniciarSesion.html.jinja", {"request": request})



@app.post('/iniciar_sesion', response_class=HTMLResponse)
async def iniciar_sesion_post(request: Request,
                   correo_electronico: str = Form(...),               
                   contrasena: str = Form(...), 
                   db: Session = Depends(get_db)):
    user = auth.autenticar_usuario(db, correo_electronico, contrasena)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Error, Incorrect username or password',
            headers={"WWW-Authenticate": "Bearer"}
        )
    tiempo_expiracion = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    nombre= f'{user.nombre} {user.apellido}'
    token_acceso = auth.crear_token_acceso(
        data={'cedula_identidad': user.cedula_identidad,
              'nombre': nombre,
              'tipo_usuario': user.tipo_usuario},
        expires_delta=tiempo_expiracion
    )
    request.session['cedula_identidad'] = user.cedula_identidad
    request.session['tipo_usuario'] = user.tipo_usuario
    
    if user.tipo_usuario == "Cliente":
        return RedirectResponse(url="/base/cliente/", status_code=status.HTTP_303_SEE_OTHER)
    elif user.tipo_usuario == "Artesano":
        return RedirectResponse(url="/base/artesano/", status_code=status.HTTP_303_SEE_OTHER)
    else:
        print("user", user.tipo_usuario )
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


#Producto

#Codigo de imagen de producto


@app.get("/productos", response_class=HTMLResponse)
async def list_productos(request: Request, db: Session = Depends(get_db)):
    productos = crudP.get_productos(db)
    return templates.TemplateResponse("productos.html", {"request": request, "productos": productos})

@app.post("/carrito/add/{producto_id}", response_class=HTMLResponse)
async def add_to_cart(request: Request, producto_id: int, db: Session = Depends(get_db)):
    producto = crudP.get_producto(db, producto_id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    carrito = request.session.get("carrito", [])
    carrito.append({"id": producto.id, "nombre": producto.nombre, "precio": producto.precio})
    request.session["carrito"] = carrito

    return templates.TemplateResponse("carrito.html", {"request": request, "carrito": carrito})

@app.get("/carrito", response_class=HTMLResponse)
async def view_cart(request: Request):
    carrito = request.session.get("carrito", [])
    return templates.TemplateResponse("carrito.html", {"request": request, "carrito": carrito})