from fastapi import APIRouter, HTTPException, Depends
from typing import List
from pydantic import BaseModel
import json
import pandas as pd
from backend.dominio.entidades.flujo_limpieza import ReglaLimpieza
from backend.infraestructura.adaptadores.motor_pandas import MotorPandas
from backend.infraestructura.adaptadores.db_sqlite_conexiones import RepositorioConexionesSQLite

router = APIRouter(prefix="/procesamiento", tags=["procesamiento"])

def get_repo_conexiones():
    return RepositorioConexionesSQLite()

class FlujoRequest(BaseModel):
    conexion_id: int
    reglas: List[ReglaLimpieza]

@router.post("/ejecutar_flujo")
def ejecutar_flujo(request: FlujoRequest, repo: RepositorioConexionesSQLite = Depends(get_repo_conexiones)):
    conexion = repo.obtener_por_id(request.conexion_id)
    if not conexion:
        raise HTTPException(status_code=404, detail="Conexión no encontrada")
    
    motor = MotorPandas()
    try:
        # Inyectar configuración de Base B si la regla es de cruce
        for regla in request.reglas:
            if regla.tipo == "cruce_bases":
                id_B = regla.parametros.get("conexion_id_B")
                if id_B:
                    conn_B = repo.obtener_por_id(id_B)
                    if conn_B:
                        regla.parametros["conexion_B_config"] = conn_B.configuracion

        df = motor.cargar_datos(conexion.configuracion)
        df_limpio = motor.aplicar_reglas(df, request.reglas)
        df_json = df_limpio.to_json(orient="records", date_format="iso")
        return {"data": json.loads(df_json)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
