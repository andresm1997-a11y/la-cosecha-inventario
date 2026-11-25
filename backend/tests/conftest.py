"""Configuracion de las pruebas: base de datos en memoria y cliente de la API."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

# SQLite en memoria compartida entre todas las conexiones de la prueba.
engine_pruebas = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
SesionPruebas = sessionmaker(bind=engine_pruebas, autoflush=False, autocommit=False)


@pytest.fixture()
def client():
    Base.metadata.create_all(bind=engine_pruebas)

    def _get_db():
        db = SesionPruebas()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _get_db
    # Sin 'with' no se ejecuta el lifespan, asi que no se toca la base real.
    cliente = TestClient(app)
    try:
        yield cliente
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine_pruebas)


@pytest.fixture()
def producto(client):
    respuesta = client.post(
        "/api/v1/productos",
        json={
            "sku": "ARR-001",
            "nombre": "Arroz Diana 500 g",
            "categoria": "Granos",
            "precio": 3200,
            "stock_actual": 20,
            "stock_minimo": 10,
        },
    )
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()
