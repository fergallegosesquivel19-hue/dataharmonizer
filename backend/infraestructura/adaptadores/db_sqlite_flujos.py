import sqlite3
import json
import os
from typing import List, Optional
from backend.dominio.puertos.repositorio_flujos import RepositorioFlujos
from backend.dominio.entidades.flujo_limpieza import FlujoLimpieza, ReglaLimpieza

class RepositorioFlujosSQLite(RepositorioFlujos):
    def __init__(self, db_path: str = None):
        if db_path is None:
            data_dir = os.getenv("DATA_DIR", ".")
            self.db_path = os.path.join(data_dir, "flujos.db")
        else:
            self.db_path = db_path
            
        self._inicializar_bd()

    def _inicializar_bd(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS flujos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    conexion_origen_id INTEGER NOT NULL,
                    reglas_json TEXT NOT NULL,
                    cron_expresion TEXT,
                    usuario_id INTEGER NOT NULL
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS logs_ejecucion (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    flujo_id INTEGER NOT NULL,
                    fecha_ejecucion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    estado TEXT NOT NULL,
                    ruta_resultado TEXT,
                    detalles TEXT
                )
            ''')
            conn.commit()

    def guardar(self, flujo: FlujoLimpieza) -> FlujoLimpieza:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            reglas_json = json.dumps([r.model_dump() for r in flujo.reglas])
            
            cursor.execute('''
                INSERT INTO flujos (nombre, conexion_origen_id, reglas_json, cron_expresion, usuario_id)
                VALUES (?, ?, ?, ?, ?)
            ''', (flujo.nombre, flujo.conexion_origen_id, reglas_json, flujo.cron_expresion, flujo.usuario_id))
            
            flujo.id = cursor.lastrowid
            conn.commit()
            return flujo

    def obtener_por_id(self, flujo_id: int) -> Optional[FlujoLimpieza]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, nombre, conexion_origen_id, reglas_json, cron_expresion, usuario_id FROM flujos WHERE id = ?', (flujo_id,))
            row = cursor.fetchone()
            if row:
                reglas_dicts = json.loads(row[3])
                reglas = [ReglaLimpieza(**r) for r in reglas_dicts]
                return FlujoLimpieza(
                    id=row[0],
                    nombre=row[1],
                    conexion_origen_id=row[2],
                    reglas=reglas,
                    cron_expresion=row[4],
                    usuario_id=row[5]
                )
        return None

    def obtener_por_usuario(self, usuario_id: int) -> List[FlujoLimpieza]:
        flujos = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, nombre, conexion_origen_id, reglas_json, cron_expresion, usuario_id FROM flujos WHERE usuario_id = ?', (usuario_id,))
            rows = cursor.fetchall()
            for row in rows:
                reglas_dicts = json.loads(row[3])
                reglas = [ReglaLimpieza(**r) for r in reglas_dicts]
                flujos.append(FlujoLimpieza(
                    id=row[0],
                    nombre=row[1],
                    conexion_origen_id=row[2],
                    reglas=reglas,
                    cron_expresion=row[4],
                    usuario_id=row[5]
                ))
        return flujos

    def obtener_todos(self) -> List[FlujoLimpieza]:
        flujos = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, nombre, conexion_origen_id, reglas_json, cron_expresion, usuario_id FROM flujos')
            rows = cursor.fetchall()
            for row in rows:
                reglas_dicts = json.loads(row[3])
                reglas = [ReglaLimpieza(**r) for r in reglas_dicts]
                flujos.append(FlujoLimpieza(
                    id=row[0],
                    nombre=row[1],
                    conexion_origen_id=row[2],
                    reglas=reglas,
                    cron_expresion=row[4],
                    usuario_id=row[5]
                ))
        return flujos

    def actualizar(self, flujo: FlujoLimpieza) -> FlujoLimpieza:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            reglas_json = json.dumps([r.model_dump() for r in flujo.reglas])
            cursor.execute('''
                UPDATE flujos 
                SET nombre = ?, conexion_origen_id = ?, reglas_json = ?, cron_expresion = ?
                WHERE id = ? AND usuario_id = ?
            ''', (flujo.nombre, flujo.conexion_origen_id, reglas_json, flujo.cron_expresion, flujo.id, flujo.usuario_id))
            conn.commit()
            return flujo

    def eliminar(self, flujo_id: int) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM flujos WHERE id = ?', (flujo_id,))
            conn.commit()
            return cursor.rowcount > 0
            
    def guardar_log(self, flujo_id: int, estado: str, ruta_resultado: str = None, detalles: str = None):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO logs_ejecucion (flujo_id, estado, ruta_resultado, detalles)
                VALUES (?, ?, ?, ?)
            ''', (flujo_id, estado, ruta_resultado, detalles))
            conn.commit()
