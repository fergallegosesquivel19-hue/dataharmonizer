from abc import ABC, abstractmethod
from typing import Optional, List
from backend.dominio.entidades.usuario import Usuario

class RepositorioUsuarios(ABC):
    @abstractmethod
    def guardar(self, usuario: Usuario) -> Usuario:
        pass

    @abstractmethod
    def obtener_por_email(self, email: str) -> Optional[Usuario]:
        pass

    @abstractmethod
    def obtener_por_id(self, id: int) -> Optional[Usuario]:
        pass

    @abstractmethod
    def eliminar(self, id: int) -> bool:
        pass

    @abstractmethod
    def obtener_todos(self) -> List[Usuario]:
        pass
