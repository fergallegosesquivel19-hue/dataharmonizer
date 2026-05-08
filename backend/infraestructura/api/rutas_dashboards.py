from fastapi import APIRouter, HTTPException
from typing import List
import os
import pandas as pd
import json

router = APIRouter(prefix="/dashboards", tags=["dashboards"])

@router.get("/archivos/all", response_model=List[str])
def listar_todos_archivos_procesados():
    archivos = []
    base_dir = os.path.join(os.getenv("DATA_DIR", "."), "uploads")
    if not os.path.exists(base_dir):
        return archivos
        
    for user_dir in os.listdir(base_dir):
        processed_dir = os.path.join(base_dir, user_dir, "processed")
        if os.path.isdir(processed_dir):
            for f in os.listdir(processed_dir):
                if f.endswith(".xlsx"):
                    archivos.append(f"{user_dir}/{f}")
    return archivos

@router.get("/archivos/{usuario_id}", response_model=List[str])
def listar_archivos_procesados(usuario_id: int):
    processed_dir = os.path.join(os.getenv("DATA_DIR", "."), "uploads", str(usuario_id), "processed")
    if not os.path.exists(processed_dir):
        return []
    
    archivos = [f for f in os.listdir(processed_dir) if f.endswith(".xlsx")]
    return archivos

@router.get("/datos/{usuario_id}/{nombre_archivo:path}")
def obtener_datos_archivo(usuario_id: str, nombre_archivo: str):
    # Seguridad: evitar path traversal malicioso
    if ".." in nombre_archivo:
        raise HTTPException(status_code=400, detail="Nombre de archivo inválido")
        
    if usuario_id == "all":
        # En este caso, nombre_archivo ya trae la forma "user_id/archivo.xlsx"
        # Inyectar 'processed' en el path para que quede DATA_DIR/uploads/user_id/processed/archivo.xlsx
        partes = nombre_archivo.split("/", 1)
        if len(partes) == 2:
            ruta_archivo = os.path.join(os.getenv("DATA_DIR", "."), "uploads", partes[0], "processed", partes[1])
        else:
            raise HTTPException(status_code=400, detail="Formato de archivo global inválido")
    else:
        ruta_archivo = os.path.join(os.getenv("DATA_DIR", "."), "uploads", str(usuario_id), "processed", nombre_archivo)
    
    if not os.path.exists(ruta_archivo):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
        
    try:
        df = pd.read_excel(ruta_archivo)
        df_json = df.to_json(orient="records", date_format="iso")
        return {"data": json.loads(df_json)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
