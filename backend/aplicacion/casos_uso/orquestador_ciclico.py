from backend.dominio.entidades.flujo_limpieza import FlujoLimpieza
from backend.aplicacion.casos_uso.ejecucion_flujos import ServicioEjecucionFlujos

class ServicioOrquestadorCiclico:
    def __init__(self, servicio_ejecucion: ServicioEjecucionFlujos):
        self.servicio_ejecucion = servicio_ejecucion
        # Dependencia a un planificador o scheduler inyectada en infraestructura

    def programar_flujo(self, flujo: FlujoLimpieza, scheduler_adapter):
        if not flujo.cron_expresion:
            raise ValueError("El flujo no tiene una expresión cron para ser programado.")
        
        # scheduler_adapter.add_job(...) se llamaría aquí en la implementación real
        pass

    def cancelar_flujo(self, flujo_id: int, scheduler_adapter):
        pass
