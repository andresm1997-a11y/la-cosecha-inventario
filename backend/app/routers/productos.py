"""Endpoints del catalogo de productos."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Producto
from ..schemas import PaginaProductos, ProductoCreate, ProductoOut, ProductoUpdate

router = APIRouter(prefix="/productos", tags=["Productos"])


def _obtener_producto(db: Session, producto_id: int) -> Producto:
    producto = db.get(Producto, producto_id)
    if producto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existe un producto con id {producto_id}",
        )
    return producto


@router.get("", response_model=PaginaProductos, summary="Listar productos")
def listar_productos(
    search: str | None = Query(default=None, description="Filtra por nombre o SKU"),
    categoria: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    consulta = select(Producto).where(Producto.activo.is_(True))

    if search:
        patron = f"%{search.strip()}%"
        consulta = consulta.where(
            or_(Producto.nombre.ilike(patron), Producto.sku.ilike(patron))
        )
    if categoria:
        consulta = consulta.where(Producto.categoria == categoria)

    total = db.scalar(select(func.count()).select_from(consulta.subquery())) or 0
    items = db.scalars(
        consulta.order_by(Producto.nombre).offset((page - 1) * size).limit(size)
    ).all()

    return PaginaProductos(items=list(items), total=total, page=page, size=size)


@router.get("/{producto_id}", response_model=ProductoOut, summary="Consultar un producto")
def consultar_producto(producto_id: int, db: Session = Depends(get_db)):
    return _obtener_producto(db, producto_id)


@router.post(
    "",
    response_model=ProductoOut,
    status_code=status.HTTP_201_CREATED,
    summary="Crear producto",
)
def crear_producto(datos: ProductoCreate, db: Session = Depends(get_db)):
    sku = datos.sku.strip().upper()
    existe = db.scalars(select(Producto).where(Producto.sku == sku)).first()
    if existe is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un producto con el SKU {sku}",
        )

    producto = Producto(
        sku=sku,
        nombre=datos.nombre.strip(),
        categoria=datos.categoria,
        imagen_url=datos.imagen_url,
        precio=datos.precio,
        stock_actual=datos.stock_actual,
        stock_minimo=datos.stock_minimo,
    )
    db.add(producto)
    db.commit()
    db.refresh(producto)
    return producto


@router.put("/{producto_id}", response_model=ProductoOut, summary="Actualizar producto")
def actualizar_producto(
    producto_id: int, datos: ProductoUpdate, db: Session = Depends(get_db)
):
    producto = _obtener_producto(db, producto_id)

    cambios = datos.model_dump(exclude_unset=True)
    for campo, valor in cambios.items():
        if valor is not None:
            setattr(producto, campo, valor)

    db.commit()
    db.refresh(producto)
    return producto


@router.delete("/{producto_id}", response_model=ProductoOut, summary="Desactivar producto")
def desactivar_producto(producto_id: int, db: Session = Depends(get_db)):
    """No se borra fisicamente: se marca inactivo para no perder el historial."""
    producto = _obtener_producto(db, producto_id)
    producto.activo = False
    db.commit()
    db.refresh(producto)
    return producto
