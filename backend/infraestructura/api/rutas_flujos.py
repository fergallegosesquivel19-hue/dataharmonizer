from fastapi import APIRouter, HTTPException, Depends
from typing import List
from pydantic import BaseModel
from backend.dominio.entidades.flujo_limpieza import FlujoLimpieza
from backend.infraestructura.adaptadores.db_sqlite_flujos import RepositorioFlujosSQLite
from backend.aplicacion.servicios.orquestador import Orquestador

router = APIRouter(prefix="/flujos", tags=["flujos"])

def get_repo_flujos():
    return RepositorioFlujosSQLite()

def get_orquestador():
    return Orquestador()

@router.post("/", response_model=FlujoLimpieza)
def guardar_flujo(flujo: FlujoLimpieza, repo: RepositorioFlujosSQLite = Depends(get_repo_flujos)):
    return repo.guardar(flujo)

@router.get("/all", response_model=List[FlujoLimpieza])
def listar_todos_flujos(repo: RepositorioFlujosSQLite = Depends(get_repo_flujos)):
    return repo.obtener_todos()

@router.get("/usuario/{usuario_id}", response_model=List[FlujoLimpieza])
def listar_flujos(usuario_id: int, repo: RepositorioFlujosSQLite = Depends(get_repo_flujos)):
    return repo.obtener_por_usuario(usuario_id)

class ProgramarRequest(BaseModel):
    cron_expresion: str

@router.post("/{flujo_id}/programar")
def programar_flujo(flujo_id: int, request: ProgramarRequest, repo: RepositorioFlujosSQLite = Depends(get_repo_flujos), orquestador: Orquestador = Depends(get_orquestador)):
    flujo = repo.obtener_por_id(flujo_id)
    if not flujo:
        raise HTTPException(status_code=404, detail="Flujo no encontrado")
        
    # Programar en APScheduler
    try:
        orquestador.programar_flujo(flujo_id, request.cron_expresion)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Expresión cron inválida: {e}")
        
    # Guardar en DB la expresión cron actualizada
    flujo.cron_expresion = request.cron_expresion
    repo.actualizar(flujo)
    
    return {"mensaje": "Flujo programado exitosamente", "cron": request.cron_expresion}

@router.post("/{flujo_id}/detener")
def detener_flujo(flujo_id: int, repo: RepositorioFlujosSQLite = Depends(get_repo_flujos), orquestador: Orquestador = Depends(get_orquestador)):
    flujo = repo.obtener_por_id(flujo_id)
    if not flujo:
        raise HTTPException(status_code=404, detail="Flujo no encontrado")
        
    orquestador.cancelar_flujo(flujo_id)
    flujo.cron_expresion = None
    repo.actualizar(flujo)
    
    return {"mensaje": "Flujo detenido"}

@router.get("/orquestador/trabajos")
def listar_trabajos(orquestador: Orquestador = Depends(get_orquestador)):
    return orquestador.obtener_trabajos()
