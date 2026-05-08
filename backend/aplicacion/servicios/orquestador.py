import os
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pandas as pd

from backend.infraestructura.adaptadores.db_sqlite_flujos import RepositorioFlujosSQLite
from backend.infraestructura.adaptadores.db_sqlite_conexiones import RepositorioConexionesSQLite
from backend.infraestructura.adaptadores.motor_pandas import MotorPandas

def ejecutar_tarea_flujo(flujo_id: int):
    repo_flujos = RepositorioFlujosSQLite()
    repo_conexiones = RepositorioConexionesSQLite()
    motor = MotorPandas()
    
    try:
        flujo = repo_flujos.obtener_por_id(flujo_id)
        if not flujo:
            raise ValueError(f"Flujo {flujo_id} no encontrado")
            
        conexion = repo_conexiones.obtener_por_id(flujo.conexion_origen_id)
        if not conexion:
            raise ValueError(f"Conexión origen {flujo.conexion_origen_id} no encontrada")
            
        # Inyectar configuración de Base B si hay cruce
        for regla in flujo.reglas:
            if regla.tipo == "cruce_bases":
                id_B = regla.parametros.get("conexion_id_B")
                if id_B:
                    conn_B = repo_conexiones.obtener_por_id(id_B)
                    if conn_B:
                        regla.parametros["conexion_B_config"] = conn_B.configuracion

        # Ejecutar limpieza
        df = motor.cargar_datos(conexion.configuracion)
        df_limpio = motor.aplicar_reglas(df, flujo.reglas)
        
        # Exportar a Excel
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_limpio = "".join(c if c.isalnum() else "_" for c in flujo.nombre).lower()
        nombre_archivo = f"flujo_{nombre_limpio}_{timestamp}.xlsx"
        
        ruta_salida = os.path.join("uploads", "processed", nombre_archivo)
        os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
        
        df_limpio.to_excel(ruta_salida, index=False)
        
        # Guardar Log exitoso
        repo_flujos.guardar_log(flujo_id, "EXITO", ruta_salida, "Procesado correctamente")
        
    except Exception as e:
        # Guardar Log de error
        repo_flujos.guardar_log(flujo_id, "ERROR", None, str(e))


class Orquestador:
    _instancia = None
    
    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super(Orquestador, cls).__new__(cls)
            cls._instancia.scheduler = BackgroundScheduler()
            cls._instancia.scheduler.start()
        return cls._instancia
        
    def programar_flujo(self, flujo_id: int, cron_expresion: str):
        # Cancelar si ya existía para reprogramar
        job_id = f"flujo_{flujo_id}"
        self.cancelar_flujo(flujo_id)
        
        trigger = CronTrigger.from_crontab(cron_expresion)
        self.scheduler.add_job(
            func=ejecutar_tarea_flujo,
            trigger=trigger,
            args=[flujo_id],
            id=job_id,
            replace_existing=True
        )
        
    def cancelar_flujo(self, flujo_id: int):
        job_id = f"flujo_{flujo_id}"
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)
            
    def obtener_trabajos(self):
        jobs = self.scheduler.get_jobs()
        return [{"id": j.id, "next_run_time": j.next_run_time.isoformat() if j.next_run_time else None} for j in jobs]

    def detener(self):
        if self.scheduler.running:
            self.scheduler.shutdown()
