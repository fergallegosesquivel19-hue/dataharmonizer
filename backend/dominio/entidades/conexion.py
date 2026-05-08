from pydantic import BaseModel
from typing import Optional, Dict, Any
from enum import Enum

class TipoConexion(str, Enum):
    SQL_SERVER = "SQL_SERVER"
    POSTGRESQL = "POSTGRESQL"
    EXCEL = "EXCEL"

class Conexion(BaseModel):
    id: Optional[int] = None
    nombre: str
    tipo: TipoConexion
    configuracion: Dict[str, Any]
    usuario_id: int
