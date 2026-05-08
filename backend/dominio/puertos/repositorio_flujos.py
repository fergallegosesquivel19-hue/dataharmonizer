from abc import ABC, abstractmethod
from typing import List, Optional
from backend.dominio.entidades.flujo_limpieza import FlujoLimpieza

class RepositorioFlujos(ABC):
    @abstractmethod
    def guardar(self, flujo: FlujoLimpieza) -> FlujoLimpieza:
        pass

    @abstractmethod
    def obtener_por_id(self, flujo_id: int) -> Optional[FlujoLimpieza]:
        pass

    @abstractmethod
    def obtener_por_usuario(self, usuario_id: int) -> List[FlujoLimpieza]:
        pass

    @abstractmethod
    def actualizar(self, flujo: FlujoLimpieza) -> FlujoLimpieza:
        pass

    @abstractmethod
    def eliminar(self, flujo_id: int) -> bool:
        pass
