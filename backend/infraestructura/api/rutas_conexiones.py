from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from typing import List
import os
import shutil
import json
import pandas as pd
from backend.dominio.entidades.conexion import Conexion, TipoConexion
from backend.infraestructura.adaptadores.db_sqlite_conexiones import RepositorioConexionesSQLite
from backend.infraestructura.adaptadores.motor_pandas import MotorPandas

router = APIRouter(prefix="/conexiones", tags=["conexiones"])

def get_repo_conexiones():
    return RepositorioConexionesSQLite()

UPLOAD_DIR_ORIGINAL = "uploads/original"
UPLOAD_DIR_WORKING = "uploads/working"

os.makedirs(UPLOAD_DIR_ORIGINAL, exist_ok=True)
os.makedirs(UPLOAD_DIR_WORKING, exist_ok=True)

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...), 
    usuario_id: int = Form(...),
    repo: RepositorioConexionesSQLite = Depends(get_repo_conexiones)
):
    try:
        original_path = os.path.join(UPLOAD_DIR_ORIGINAL, file.filename)
        with open(original_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        working_filename = f"working_{file.filename}"
        working_path = os.path.join(UPLOAD_DIR_WORKING, working_filename)
        shutil.copyfile(original_path, working_path)
        
        conexion = Conexion(
            nombre=f"Archivo: {file.filename}",
            tipo=TipoConexion.EXCEL,
            configuracion={
                "ruta_archivo": working_path,
                "ruta_original": original_path
            },
            usuario_id=usuario_id
        )
        return repo.guardar(conexion)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/usuario/{usuario_id}", response_model=List[Conexion])
def listar_conexiones(usuario_id: int, repo: RepositorioConexionesSQLite = Depends(get_repo_conexiones)):
    return repo.obtener_todas_por_usuario(usuario_id)

@router.get("/{id}/datos")
def obtener_datos(id: int, repo: RepositorioConexionesSQLite = Depends(get_repo_conexiones)):
    conexion = repo.obtener_por_id(id)
    if not conexion:
        raise HTTPException(status_code=404, detail="Conexión no encontrada")
    
    motor = MotorPandas()
    try:
        df = motor.cargar_datos(conexion.configuracion)
        df_json = df.to_json(orient="records", date_format="iso")
        return {"data": json.loads(df_json)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{id}/datos")
def guardar_datos(id: int, payload: dict, repo: RepositorioConexionesSQLite = Depends(get_repo_conexiones)):
    conexion = repo.obtener_por_id(id)
    if not conexion:
        raise HTTPException(status_code=404, detail="Conexión no encontrada")
    
    try:
        df = pd.DataFrame(payload["data"])
        motor = MotorPandas()
        motor.guardar_resultados(df, conexion.configuracion)
        return {"mensaje": "Datos actualizados en la copia de trabajo."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
