import sqlite3
from typing import Optional, List
from backend.dominio.entidades.usuario import Usuario
from backend.dominio.puertos.repositorio_usuarios import RepositorioUsuarios

class RepositorioUsuariosSQLite(RepositorioUsuarios):
    def __init__(self, db_path: str = "usuarios.db"):
        self.db_path = db_path
        self._inicializar_db()

    def _inicializar_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    nombre TEXT NOT NULL,
                    password_hash TEXT NOT NULL,
                    es_admin BOOLEAN NOT NULL CHECK (es_admin IN (0, 1))
                )
            ''')

    def guardar(self, usuario: Usuario) -> Usuario:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO usuarios (email, nombre, password_hash, es_admin) VALUES (?, ?, ?, ?)",
                (usuario.email, usuario.nombre, usuario.password_hash, int(usuario.es_admin))
            )
            usuario.id = cursor.lastrowid
            return usuario

    def obtener_por_email(self, email: str) -> Optional[Usuario]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, email, nombre, password_hash, es_admin FROM usuarios WHERE email = ?", (email,))
            row = cursor.fetchone()
            if row:
                return Usuario(id=row[0], email=row[1], nombre=row[2], password_hash=row[3], es_admin=bool(row[4]))
            return None

    def obtener_por_id(self, id: int) -> Optional[Usuario]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, email, nombre, password_hash, es_admin FROM usuarios WHERE id = ?", (id,))
            row = cursor.fetchone()
            if row:
                return Usuario(id=row[0], email=row[1], nombre=row[2], password_hash=row[3], es_admin=bool(row[4]))
            return None

    def eliminar(self, id: int) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM usuarios WHERE id = ?", (id,))
            return cursor.rowcount > 0

    def obtener_todos(self) -> List[Usuario]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, email, nombre, password_hash, es_admin FROM usuarios")
            rows = cursor.fetchall()
            return [Usuario(id=row[0], email=row[1], nombre=row[2], password_hash=row[3], es_admin=bool(row[4])) for row in rows]
