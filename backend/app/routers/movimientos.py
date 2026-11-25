"""Endpoints de movimientos de inventario.

Aqui vive la regla de negocio central del sistema: una salida nunca puede
dejar el stock en negativo, y el descuento del stock junto con el registro
del movimiento ocurren en una sola transaccion.
"""

from datetime import date, datetime, time

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Movimiento, Producto
from ..schemas import (
    MovimientoCreate,
    MovimientoOut,
    MovimientoResultado,
    PaginaMovimientos,
)

router = APIRouter(prefix="/movimientos", tags=["Movimientos"])


@router.post(
    "",
    response_model=MovimientoResultado,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar una entrada o una salida",
)
def registrar_movimiento(datos: MovimientoCreate, db: Session = Depends(get_db)):
    # Bloquea la fila mientras se calcula el nuevo stock (en PostgreSQL).
    producto = db.scalars(
        select(Producto).where(Producto.id == datos.producto_id).with_for_update()
    ).first()

    if producto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existe un producto con id {datos.producto_id}",
        )
    if not producto.activo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El producto esta inactivo y no admite movimientos",
        )
    if datos.tipo == "salida" and datos.cantidad > producto.stock_actual:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Stock insuficiente: hay {producto.stock_actual} unidades "
                f"de {producto.sku} y se intentan retirar {datos.cantidad}"
            ),
        )

    if datos.tipo == "entrada":
        producto.stock_actual += datos.cantidad
    else:
        producto.stock_actual -= datos.cantidad

    movimiento = Movimiento(
        producto_id=producto.id,
        tipo=datos.tipo,
        cantidad=datos.cantidad,
        motivo=datos.motivo,
    )
    db.add(movimiento)

    try:
        # Un solo commit: stock y movimiento quedan consistentes o no queda nada.
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(movimiento)
    db.refresh(producto)
    return MovimientoResultado(movimiento=movimiento, stock_resultante=producto.stock_actual)


@router.get("", response_model=PaginaMovimientos, summary="Listar movimientos")
def listar_movimientos(
    producto_id: int | None = Query(default=None),
    desde: date | None = Query(default=None, description="Fecha inicial (AAAA-MM-DD)"),
    hasta: date | None = Query(default=None, description="Fecha final (AAAA-MM-DD)"),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    consulta = select(Movimiento)

    if producto_id is not None:
        consulta = consulta.where(Movimiento.producto_id == producto_id)
    if desde is not None:
        consulta = consulta.where(Movimiento.fecha >= datetime.combine(desde, time.min))
    if hasta is not None:
        consulta = consulta.where(Movimiento.fecha <= datetime.combine(hasta, time.max))

    total = db.scalar(select(func.count()).select_from(consulta.subquery())) or 0
    items = db.scalars(
        consulta.order_by(Movimiento.fecha.desc(), Movimiento.id.desc())
        .offset((page - 1) * size)
        .limit(size)
    ).all()

    return PaginaMovimientos(items=list(items), total=total, page=page, size=size)
