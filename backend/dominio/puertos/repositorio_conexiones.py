from abc import ABC, abstractmethod
from typing import List, Optional
from backend.dominio.entidades.conexion import Conexion

class RepositorioConexiones(ABC):
    @abstractmethod
    def guardar(self, conexion: Conexion) -> Conexion:
        pass

    @abstractmethod
    def obtener_todas_por_usuario(self, usuario_id: int) -> List[Conexion]:
        pass

    @abstractmethod
    def obtener_por_id(self, conexion_id: int) -> Optional[Conexion]:
        pass
