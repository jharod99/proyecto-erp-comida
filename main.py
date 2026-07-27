import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from database import engine, Base
from routers import menu, orders, admin, kds

# Crear tablas en SQLite al iniciar
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Proyecto Coconut - API Juguería Saludable",
    description="Sistema de gestión y ventas para juguería saludable basado en Excelencia Operacional y Poka-Yokes.",
    version="1.0.0"
)

# Inclusión de Routers de API Backend
app.include_router(menu.router)
app.include_router(orders.router)
app.include_router(admin.router)
app.include_router(kds.router)

# Montar archivos estáticos del Frontend
frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/frontend", StaticFiles(directory=frontend_dir, html=True), name="frontend")


@app.get("/")
def read_root():
    """Redirige automáticamente al prototipo frontend del cliente."""
    return RedirectResponse(url="/frontend/index.html")