from abc import ABC, abstractmethod
from typing import Any, List
from backend.dominio.entidades.flujo_limpieza import ReglaLimpieza

class MotorProcesamiento(ABC):
    @abstractmethod
    def cargar_datos(self, conexion_config: dict) -> Any:
        pass
        
    @abstractmethod
    def aplicar_reglas(self, datos: Any, reglas: List[ReglaLimpieza]) -> Any:
        pass

    @abstractmethod
    def guardar_resultados(self, datos: Any, destino_config: dict) -> None:
        pass
