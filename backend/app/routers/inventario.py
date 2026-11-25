"""Consulta consolidada del inventario."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Producto
from ..schemas import StockItem, StockResumen

router = APIRouter(prefix="/inventario", tags=["Inventario"])


@router.get("/stock", response_model=StockResumen, summary="Stock consolidado")
def consultar_stock(db: Session = Depends(get_db)):
    """Devuelve el stock por producto y los totales del inventario.

    El calculo se hace en el servidor con una sola consulta, en lugar de
    enviar todo el historial al navegador para que lo sume.
    """
    productos = db.scalars(
        select(Producto).where(Producto.activo.is_(True)).order_by(Producto.nombre)
    ).all()

    items: list[StockItem] = []
    for p in productos:
        items.append(
            StockItem(
                id=p.id,
                sku=p.sku,
                nombre=p.nombre,
                categoria=p.categoria,
                imagen_url=p.imagen_url,
                stock_actual=p.stock_actual,
                stock_minimo=p.stock_minimo,
                stock_bajo=p.stock_actual <= p.stock_minimo,
                valor=round(float(p.precio) * p.stock_actual, 2),
            )
        )

    return StockResumen(
        items=items,
        total_productos=len(items),
        total_unidades=sum(i.stock_actual for i in items),
        valor_total=round(sum(i.valor for i in items), 2),
        productos_bajo_stock=sum(1 for i in items if i.stock_bajo),
    )
