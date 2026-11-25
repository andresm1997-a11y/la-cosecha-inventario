"""Conexion a la base de datos.

En desarrollo se usa SQLite; en produccion (Render) se usa PostgreSQL a traves
de la variable de entorno DATABASE_URL. El mismo codigo sirve para ambas.
"""

import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

BASE_DIR = Path(__file__).resolve().parent.parent


def _normalizar(url: str) -> str:
    """Render entrega 'postgres://' y SQLAlchemy 2 exige 'postgresql://'."""
    if url.startswith("postgres://"):
        return "postgresql://" + url[len("postgres://"):]
    return url


DATABASE_URL = _normalizar(os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'inventario.db'}"))

_conexion = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# pool_pre_ping evita errores por conexiones que el proveedor cerro por inactividad.
engine = create_engine(DATABASE_URL, connect_args=_conexion, pool_pre_ping=True, future=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


class Base(DeclarativeBase):
    """Clase base declarativa de todos los modelos."""


def get_db():
    """Dependencia de FastAPI: entrega una sesion y la cierra al terminar."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
