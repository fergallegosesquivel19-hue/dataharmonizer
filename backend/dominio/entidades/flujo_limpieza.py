from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class ReglaLimpieza(BaseModel):
    tipo: str
    parametros: Dict[str, Any]

class FlujoLimpieza(BaseModel):
    id: Optional[int] = None
    nombre: str
    conexion_origen_id: int
    reglas: List[ReglaLimpieza]
    cron_expresion: Optional[str] = None
    usuario_id: int
