from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from datetime import timedelta
from sqlalchemy.orm import Session
from db.db_config import SessionLocal, engine 
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from datetime import datetime
from fastapi.responses import RedirectResponse, HTMLResponse, Response
#from tipos_usuario.service import listar_todos_los_tipos_de_usuarios
from schemas import Token, Respuesta
import models, schemas
#from usuarios.service import AuthHandler, Requires_el_Login_de_Exception, eliminar_el_usuario

models.Base.metadata.create_all(bind=engine)

router = APIRouter()

auth_handler = AuthHandler()

templates = Jinja2Templates(directory="../templates/usuarios")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get('/registrar', response_class=HTMLResponse)
def registrar_el_usuario(request: Request, db: Session = Depends(get_db)):
    #lista = listar_todos_los_tipos_de_usuarios(db=db)
    return templates.TemplateResponse("registro.html", {'request': request, 'lista': lista})      

@router.post('/registrar', response_class=HTMLResponse)
def registrar_el_usuario(request: Request, 
                      id: str = Form(...), 
                      nombres: str = Form(...), 
                      apellidos: str = Form(...), 
                      correo: str = Form(...), 
                      contraseña: str = Form(...), 
                      tipo_id: int = Form(...), 
                      db: Session = Depends(get_db)):

    usuario = schemas.Usuario(
        id=id, 
        nombres=nombres, 
        apellidos=apellidos, 
        correo=correo, 
        contraseña=contraseña, 
        tipo_id=tipo_id
    )
    auth_handler.registrar_el_usuario(db=db, usuario=usuario)
    return RedirectResponse(url='/', status_code=status.HTTP_303_SEE_OTHER)


@router.get('/logout')
async def logout(request: Request, response: Response):
    response = templates.TemplateResponse("success.html", 
                    {"request": request, "nombre_completo": "", "success_msg": "laragte y no vuelvas :v",
                    "path_route": '/', "path_msg": "Inicio"})
    response.delete_cookie(key="Authorization")
    return response

@router.get("/private", response_class=HTMLResponse)
async def private(request: Request, info=Depends(auth_handler.auth_wrapper)):
    try:
        return templates.TemplateResponse("private.html", {"request": request, "info": info})
    except:
        raise Requires_el_Login_de_Exception() 
    
@router.delete('/usuario/{id}', response_model=schemas.Usuario)
def borrar_usuario(id : str, db: Session = Depends(get_db)): 
    return eliminar_el_usuario(db=db, id=id)

@router.get('/iniciar_sesion', response_class=HTMLResponse)
def registrar_el_usuario(request: Request):
    return templates.TemplateResponse(request=request, name="iniciarsesion.html")      

@router.post('/iniciar_sesion')
async def iniciar_sesion(request: Request, response: Response, id: str = Form(...), contraseña: str = Form(...),db: Session = Depends(get_db)) -> Token: 
    usuario = await auth_handler.autenticacion_del_usuario(db, id, contraseña)
    try:
        if usuario: 
            nombre_completo = f'{usuario.nombres} {usuario.apellidos}'
            atoken = auth_handler.creacion_para_el_accesso_al_token(data={'id': usuario.id, 'nombre_completo': nombre_completo, 'tipo_usuario_id': usuario.tipo_id})
            if usuario.tipo_id == 1: 
                response = templates.TemplateResponse("success.html", 
                    {"request": request, "nombre_completo": nombre_completo, "success_msg": "esta es la pagina de inicio",
                    "path_route": '/home', "path_msg": "Home"})
            elif usuario.tipo_id == 2: 
                response = templates.TemplateResponse("success.html", 
                    {"request": request, "nombre_completo": nombre_completo, "success_msg": "esta es la pagina de inicio",
                    "path_route": '/home', "path_msg": "Home"})
            else: 
                response = templates.TemplateResponse("success.html", 
                    {"request": request, "nombre_completo": nombre_completo, "success_msg": "esta es la pagina de inicio",
                    "path_route": '/home', "path_msg": "Home"})
            
            response.set_cookie(key="Authorization", value= f"{atoken}", httponly=True)
            return response
        else:
                return templates.TemplateResponse("error.html",
                {"request": request, 'detail': 'contraseña incorrecta :v', 'status_code': 404 })

    except Exception as err:
        return templates.TemplateResponse("error.html",
            {"request": request, 'detail': 'contraseña incorrecta :v', 'status_code': 401 })