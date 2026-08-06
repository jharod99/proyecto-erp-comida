import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from database import engine, Base, SessionLocal
from models import ProductoBase
from routers import menu, orders, admin, kds
from poblar_bd import poblar_base_de_datos

# Crear tablas en SQLite al iniciar
Base.metadata.create_all(bind=engine)

# Auto-poblar base de datos en inicio si está vacía (ideal para Render / producción)
db = SessionLocal()
try:
    if not db.query(ProductoBase).first():
        print("Base de datos inicial vacía detectada. Poblando automáticamente...")
        poblar_base_de_datos()
except Exception as e:
    print(f"Error al verificar/poblar DB: {e}")
finally:
    db.close()

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