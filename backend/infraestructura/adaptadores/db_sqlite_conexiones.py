import sqlite3
import json
import os
from typing import List, Optional
from backend.dominio.entidades.conexion import Conexion, TipoConexion
from backend.dominio.puertos.repositorio_conexiones import RepositorioConexiones

class RepositorioConexionesSQLite(RepositorioConexiones):
    def __init__(self, db_path: str = None):
        if db_path is None:
            data_dir = os.getenv("DATA_DIR", ".")
            self.db_path = os.path.join(data_dir, "conexiones.db")
        else:
            self.db_path = db_path
        self._inicializar_db()

    def _inicializar_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS conexiones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    tipo TEXT NOT NULL,
                    configuracion TEXT NOT NULL,
                    usuario_id INTEGER NOT NULL
                )
            ''')

    def guardar(self, conexion: Conexion) -> Conexion:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            config_str = json.dumps(conexion.configuracion)
            
            if conexion.id is None:
                cursor.execute(
                    "INSERT INTO conexiones (nombre, tipo, configuracion, usuario_id) VALUES (?, ?, ?, ?)",
                    (conexion.nombre, conexion.tipo.value, config_str, conexion.usuario_id)
                )
                conexion.id = cursor.lastrowid
            else:
                cursor.execute(
                    "UPDATE conexiones SET nombre = ?, tipo = ?, configuracion = ? WHERE id = ?",
                    (conexion.nombre, conexion.tipo.value, config_str, conexion.id)
                )
            return conexion

    def obtener_todas(self) -> List[Conexion]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, nombre, tipo, configuracion, usuario_id FROM conexiones")
            rows = cursor.fetchall()
            return [
                Conexion(
                    id=row[0], 
                    nombre=row[1], 
                    tipo=TipoConexion(row[2]), 
                    configuracion=json.loads(row[3]), 
                    usuario_id=row[4]
                ) for row in rows
            ]

    def obtener_todas_por_usuario(self, usuario_id: int) -> List[Conexion]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, nombre, tipo, configuracion, usuario_id FROM conexiones WHERE usuario_id = ?", (usuario_id,))
            rows = cursor.fetchall()
            return [
                Conexion(
                    id=row[0], 
                    nombre=row[1], 
                    tipo=TipoConexion(row[2]), 
                    configuracion=json.loads(row[3]), 
                    usuario_id=row[4]
                ) for row in rows
            ]

    def obtener_por_id(self, conexion_id: int) -> Optional[Conexion]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, nombre, tipo, configuracion, usuario_id FROM conexiones WHERE id = ?", (conexion_id,))
            row = cursor.fetchone()
            if row:
                return Conexion(
                    id=row[0], 
                    nombre=row[1], 
                    tipo=TipoConexion(row[2]), 
                    configuracion=json.loads(row[3]), 
                    usuario_id=row[4]
                )
            return None
