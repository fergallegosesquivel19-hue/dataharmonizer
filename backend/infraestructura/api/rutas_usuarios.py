from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from backend.dominio.entidades.usuario import Usuario
from backend.aplicacion.casos_uso.gestion_usuarios import ServicioGestionUsuarios
from backend.infraestructura.adaptadores.db_sqlite_usuarios import RepositorioUsuariosSQLite

router = APIRouter(prefix="/usuarios", tags=["usuarios"])

def get_servicio_usuarios():
    repo = RepositorioUsuariosSQLite()
    return ServicioGestionUsuarios(repo)

@router.post("/", response_model=Usuario)
def crear_usuario(usuario: Usuario, servicio: ServicioGestionUsuarios = Depends(get_servicio_usuarios)):
    try:
        # Note: We receive the plain password in the `password_hash` field from the client for simplicity.
        return servicio.registrar_usuario(usuario.email, usuario.nombre, usuario.password_hash, usuario.es_admin)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login", response_model=Usuario)
def login(request: LoginRequest, servicio: ServicioGestionUsuarios = Depends(get_servicio_usuarios)):
    try:
        return servicio.autenticar_usuario(request.email, request.password)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.get("/", response_model=list[Usuario])
def obtener_todos(servicio: ServicioGestionUsuarios = Depends(get_servicio_usuarios)):
    return servicio.obtener_todos()

@router.delete("/{id}")
def eliminar_usuario(id: int, tiene_flujos: bool = False, servicio: ServicioGestionUsuarios = Depends(get_servicio_usuarios)):
    try:
        eliminado = servicio.eliminar_usuario(id, tiene_flujos)
        if not eliminado:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return {"mensaje": "Usuario eliminado correctamente"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
