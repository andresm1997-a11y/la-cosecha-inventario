"""Modelos de datos del inventario.

Solo dos entidades: el catalogo (Producto) y el historial (Movimiento).
El movimiento es el eje de la trazabilidad: cada entrada o salida modifica
el stock del producto y deja registro de cuando y por que ocurrio.
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Producto(Base):
    __tablename__ = "productos"

    id: Mapped[int] = mapped_column(primary_key=True)
    sku: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    nombre: Mapped[str] = mapped_column(String(120), index=True)
    categoria: Mapped[str | None] = mapped_column(String(60), default=None)
    imagen_url: Mapped[str | None] = mapped_column(String(255), default=None)
    precio: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    stock_actual: Mapped[int] = mapped_column(Integer, default=0)
    stock_minimo: Mapped[int] = mapped_column(Integer, default=0)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    movimientos: Mapped[list["Movimiento"]] = relationship(
        back_populates="producto",
        cascade="all, delete-orphan",
    )


class Movimiento(Base):
    __tablename__ = "movimientos"

    id: Mapped[int] = mapped_column(primary_key=True)
    producto_id: Mapped[int] = mapped_column(
        ForeignKey("productos.id", ondelete="CASCADE"), index=True
    )
    tipo: Mapped[str] = mapped_column(String(10))
    cantidad: Mapped[int] = mapped_column(Integer)
    motivo: Mapped[str | None] = mapped_column(String(120), default=None)
    fecha: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    producto: Mapped[Producto] = relationship(back_populates="movimientos")
