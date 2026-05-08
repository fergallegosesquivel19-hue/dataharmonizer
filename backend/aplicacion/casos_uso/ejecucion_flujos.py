from typing import Dict, Any, List
from backend.dominio.entidades.flujo_limpieza import FlujoLimpieza
from backend.dominio.entidades.conexion import Conexion
from backend.dominio.puertos.motor_procesamiento import MotorProcesamiento
from backend.dominio.puertos.repositorio_conexiones import RepositorioConexiones

class ServicioEjecucionFlujos:
    def __init__(self, motor: MotorProcesamiento, repo_conexiones: RepositorioConexiones):
        self.motor = motor
        self.repo_conexiones = repo_conexiones

    def ejecutar_flujo(self, flujo: FlujoLimpieza, destino_config: Dict[str, Any] = None):
        conexion_origen = self.repo_conexiones.obtener_por_id(flujo.conexion_origen_id)
        if not conexion_origen:
            raise ValueError("Conexión de origen no encontrada.")

        datos = self.motor.cargar_datos(conexion_origen.configuracion)
        datos_procesados = self.motor.aplicar_reglas(datos, flujo.reglas)

        if destino_config:
            self.motor.guardar_resultados(datos_procesados, destino_config)
            
        return datos_procesados
