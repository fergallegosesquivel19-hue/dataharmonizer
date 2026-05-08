from fastapi import APIRouter, HTTPException
from typing import List
import os
import pandas as pd
import json

router = APIRouter(prefix="/dashboards", tags=["dashboards"])
PROCESSED_DIR = os.path.join("uploads", "processed")

@router.get("/archivos", response_model=List[str])
def listar_archivos_procesados():
    if not os.path.exists(PROCESSED_DIR):
        return []
    
    archivos = [f for f in os.listdir(PROCESSED_DIR) if f.endswith(".xlsx")]
    return archivos

@router.get("/datos/{nombre_archivo}")
def obtener_datos_archivo(nombre_archivo: str):
    # Seguridad: evitar path traversal
    if ".." in nombre_archivo or "/" in nombre_archivo or "\\" in nombre_archivo:
        raise HTTPException(status_code=400, detail="Nombre de archivo inválido")
        
    ruta_archivo = os.path.join(PROCESSED_DIR, nombre_archivo)
    
    if not os.path.exists(ruta_archivo):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
        
    try:
        df = pd.read_excel(ruta_archivo)
        df_json = df.to_json(orient="records", date_format="iso")
        return {"data": json.loads(df_json)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
