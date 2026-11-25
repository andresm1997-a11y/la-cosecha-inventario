"""Esquemas de entrada y salida de la API.

Aqui viven las validaciones de forma: tipos, campos obligatorios y rangos.
Las reglas de negocio (stock suficiente, producto existente) se validan en los
routers, porque necesitan consultar la base de datos.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ProductoBase(BaseModel):
    sku: str = Field(min_length=1, max_length=40, examples=["ARR-001"])
    nombre: str = Field(min_length=1, max_length=120, examples=["Arroz Diana 500 g"])
    categoria: str | None = Field(default=None, max_length=60, examples=["Granos"])
    imagen_url: str | None = Field(
        default=None,
        max_length=255,
        description="Ruta relativa servida por la API o URL absoluta",
        examples=["/static/productos/arroz.jpg"],
    )
    precio: float = Field(default=0, ge=0, examples=[3200])
    stock_minimo: int = Field(default=0, ge=0, examples=[10])


class ProductoCreate(ProductoBase):
    stock_actual: int = Field(default=0, ge=0)


class ProductoUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=120)
    categoria: str | None = Field(default=None, max_length=60)
    imagen_url: str | None = Field(default=None, max_length=255)
    precio: float | None = Field(default=None, ge=0)
    stock_minimo: int | None = Field(default=None, ge=0)
    activo: bool | None = None


class ProductoOut(ProductoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    stock_actual: int
    activo: bool


class PaginaProductos(BaseModel):
    items: list[ProductoOut]
    total: int
    page: int
    size: int


class MovimientoCreate(BaseModel):
    producto_id: int = Field(ge=1)
    tipo: Literal["entrada", "salida"]
    cantidad: int = Field(gt=0, le=1_000_000, description="Debe ser mayor que cero")
    motivo: str | None = Field(default=None, max_length=120, examples=["venta"])


class MovimientoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    producto_id: int
    tipo: str
    cantidad: int
    motivo: str | None
    fecha: datetime


class MovimientoResultado(BaseModel):
    movimiento: MovimientoOut
    stock_resultante: int


class PaginaMovimientos(BaseModel):
    items: list[MovimientoOut]
    total: int
    page: int
    size: int


class StockItem(BaseModel):
    id: int
    sku: str
    nombre: str
    categoria: str | None
    imagen_url: str | None
    stock_actual: int
    stock_minimo: int
    stock_bajo: bool
    valor: float


class StockResumen(BaseModel):
    items: list[StockItem]
    total_productos: int
    total_unidades: int
    valor_total: float
    productos_bajo_stock: int
