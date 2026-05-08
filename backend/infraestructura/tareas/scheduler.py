from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

class SchedularOrquestador:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()

    def agregar_tarea(self, id_tarea: str, funcion, cron_expr: str):
        self.scheduler.add_job(
            funcion, 
            CronTrigger.from_crontab(cron_expr), 
            id=id_tarea,
            replace_existing=True
        )

    def eliminar_tarea(self, id_tarea: str):
        if self.scheduler.get_job(id_tarea):
            self.scheduler.remove_job(id_tarea)
