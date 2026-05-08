from backend.dominio.puertos.repositorio_usuarios import RepositorioUsuarios
from backend.dominio.entidades.usuario import Usuario
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class ServicioGestionUsuarios:
    def __init__(self, repo_usuarios: RepositorioUsuarios):
        self.repo_usuarios = repo_usuarios

    def registrar_usuario(self, email: str, nombre: str, password_texto_plano: str, es_admin: bool = False) -> Usuario:
        if self.repo_usuarios.obtener_por_email(email):
            raise ValueError(f"El usuario con email {email} ya existe.")
        
        hashed_password = pwd_context.hash(password_texto_plano)
        nuevo_usuario = Usuario(email=email, nombre=nombre, password_hash=hashed_password, es_admin=es_admin)
        return self.repo_usuarios.guardar(nuevo_usuario)

    def eliminar_usuario(self, id_usuario: int, tiene_flujos_activos: bool) -> bool:
        if tiene_flujos_activos:
            raise ValueError("Atención: Está eliminando un usuario con flujos cíclicos activos. No se puede eliminar.")
        return self.repo_usuarios.eliminar(id_usuario)

    def obtener_usuario(self, id_usuario: int) -> Usuario:
        return self.repo_usuarios.obtener_por_id(id_usuario)

    def obtener_todos(self) -> list[Usuario]:
        return self.repo_usuarios.obtener_todos()

    def autenticar_usuario(self, email: str, password_texto_plano: str) -> Usuario:
        usuario = self.repo_usuarios.obtener_por_email(email)
        if not usuario:
            raise ValueError("Credenciales incorrectas.")
        if not pwd_context.verify(password_texto_plano, usuario.password_hash):
            raise ValueError("Credenciales incorrectas.")
        return usuario
