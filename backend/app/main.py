"""Punto de entrada de la API de inventarios.

Ejecutar en local:
    uvicorn app.main:app --reload --port 8000

Documentacion interactiva: http://localhost:8000/docs
"""

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .database import Base, engine
from .routers import inventario, movimientos, productos

DESCRIPCION = """
API REST del sistema de inventarios de Distribuciones La Cosecha S.A.S.

Cubre el catalogo de productos, el registro de entradas y salidas y la
consulta del stock. Las reglas de negocio se validan en el servidor:
no se admiten cantidades negativas, no se puede sacar mas de lo que hay
y un movimiento sobre un producto inexistente devuelve 404.
"""


@asynccontextmanager
async def lifespan(app: FastAPI):
    # En un proyecto mas grande esto se reemplaza por migraciones de Alembic.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Inventario La Cosecha",
    description=DESCRIPCION,
    version="1.0.0",
    lifespan=lifespan,
)

_origenes = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _origenes.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(productos.router, prefix="/api/v1")
app.include_router(movimientos.router, prefix="/api/v1")
app.include_router(inventario.router, prefix="/api/v1")

# Imagenes de producto: el backend las sirve como archivos estaticos para que
# el frontend solo guarde una ruta relativa (/static/productos/arroz.jpg).
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
STATIC_DIR.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", tags=["Salud"], summary="Estado del servicio")
def estado():
    return {
        "servicio": "Inventario La Cosecha",
        "version": "1.0.0",
        "documentacion": "/docs",
    }
