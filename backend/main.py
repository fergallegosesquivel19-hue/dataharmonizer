from fastapi import FastAPI
from contextlib import asynccontextmanager
from backend.infraestructura.api import rutas_usuarios, rutas_procesamiento, rutas_conexiones, rutas_flujos, rutas_dashboards
from backend.aplicacion.servicios.orquestador import Orquestador
from backend.infraestructura.adaptadores.db_sqlite_usuarios import RepositorioUsuariosSQLite
from backend.aplicacion.casos_uso.gestion_usuarios import ServicioGestionUsuarios

@asynccontextmanager
async def lifespan(app: FastAPI):
    repo = RepositorioUsuariosSQLite()
    servicio = ServicioGestionUsuarios(repo)
    if not repo.obtener_por_email("admin@empresa.com"):
        try:
            servicio.registrar_usuario("admin@empresa.com", "Administrador Inicial", "admin123", es_admin=True)
            print("Usuario inicial 'admin@empresa.com' creado.")
        except Exception as e:
            print(f"Error creando usuario inicial: {e}")
    # Inicializar orquestador y recuperar trabajos guardados
    orquestador = Orquestador()
    yield
    orquestador.detener()

app = FastAPI(title="Plataforma de Datos API", lifespan=lifespan)

app.include_router(rutas_usuarios.router)
app.include_router(rutas_procesamiento.router)
app.include_router(rutas_conexiones.router)
app.include_router(rutas_flujos.router)
app.include_router(rutas_dashboards.router)

@app.get("/")
def read_root():
    return {"mensaje": "API de Plataforma Empresarial de Datos"}
