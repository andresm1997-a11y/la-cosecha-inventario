"""Carga un catálogo de ejemplo para probar el sistema.

Uso (desde la carpeta backend, con el entorno activo):
    python seed.py

Es idempotente: si ya hay productos, no hace nada. El stock inicial se carga
como movimientos de entrada, de modo que el historial y el stock coincidan.

Las imágenes viven en backend/static/productos y la API las sirve en /static.
La ruta se guarda relativa para que funcione igual en local y en producción.
"""

from sqlalchemy import func, select

from app.database import Base, SessionLocal, engine
from app.models import Movimiento, Producto

CATALOGO = [
    {
        "sku": "ARR-001",
        "nombre": "Arroz Diana 500 g",
        "categoria": "Granos",
        "imagen_url": "/static/productos/arroz.jpg",
        "precio": 3200,
        "stock_inicial": 48,
        "stock_minimo": 15,
    },
    {
        "sku": "ACE-002",
        "nombre": "Aceite Girasol 1 L",
        "categoria": "Aceites",
        "imagen_url": "/static/productos/aceite.jpg",
        "precio": 8900,
        "stock_inicial": 24,
        "stock_minimo": 12,
    },
    {
        "sku": "LEC-003",
        "nombre": "Leche Entera 1 L",
        "categoria": "Lácteos",
        "imagen_url": "/static/productos/leche.jpg",
        "precio": 4100,
        "stock_inicial": 60,
        "stock_minimo": 20,
    },
    {
        "sku": "AZU-004",
        "nombre": "Azúcar Manuelita 1 kg",
        "categoria": "Abarrotes",
        "imagen_url": "/static/productos/azucar.jpg",
        "precio": 5600,
        "stock_inicial": 7,
        "stock_minimo": 10,
    },
    {
        "sku": "FRI-005",
        "nombre": "Fríjol Cargamanto 500 g",
        "categoria": "Granos",
        "imagen_url": "/static/productos/frijol.jpg",
        "precio": 6800,
        "stock_inicial": 34,
        "stock_minimo": 12,
    },
    {
        # Sin imagen a propósito: sirve para ver el marcador de posición.
        "sku": "SAL-006",
        "nombre": "Sal Refisal 500 g",
        "categoria": "Abarrotes",
        "imagen_url": None,
        "precio": 1800,
        "stock_inicial": 40,
        "stock_minimo": 10,
    },
]

# sku, tipo, cantidad, motivo
MOVIMIENTOS = [
    ("ARR-001", "salida", 12, "venta"),
    ("LEC-003", "salida", 15, "venta"),
    ("AZU-004", "salida", 2, "venta"),
    ("SAL-006", "entrada", 10, "compra"),
]


def main() -> None:
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        total = db.scalar(select(func.count()).select_from(Producto)) or 0
        if total:
            print(f"Ya existen {total} productos. No se carga nada.")
            return

        productos: dict[str, Producto] = {}
        for datos in CATALOGO:
            producto = Producto(
                sku=datos["sku"],
                nombre=datos["nombre"],
                categoria=datos["categoria"],
                imagen_url=datos["imagen_url"],
                precio=datos["precio"],
                stock_actual=0,
                stock_minimo=datos["stock_minimo"],
            )
            db.add(producto)
            db.flush()
            productos[datos["sku"]] = producto

            # El stock inicial entra como movimiento para dejar trazabilidad.
            db.add(
                Movimiento(
                    producto_id=producto.id,
                    tipo="entrada",
                    cantidad=datos["stock_inicial"],
                    motivo="carga inicial",
                )
            )
            producto.stock_actual = datos["stock_inicial"]

        for sku, tipo, cantidad, motivo in MOVIMIENTOS:
            producto = productos[sku]
            if tipo == "salida" and cantidad > producto.stock_actual:
                continue
            producto.stock_actual += cantidad if tipo == "entrada" else -cantidad
            db.add(
                Movimiento(
                    producto_id=producto.id,
                    tipo=tipo,
                    cantidad=cantidad,
                    motivo=motivo,
                )
            )

        db.commit()
        print(f"Catalogo cargado: {len(CATALOGO)} productos.")


if __name__ == "__main__":
    main()
