"""Pruebas de la API. Cada prueba corresponde a un caso del informe (CP-xx).

Ejecutar desde la carpeta backend:
    pip install -r requirements-dev.txt
    python -m pytest -v
"""


def test_cp01_crear_producto(client):
    respuesta = client.post(
        "/api/v1/productos",
        json={
            "sku": "ace-001",
            "nombre": "Aceite Girasol 1 L",
            "precio": 8900,
            "stock_actual": 5,
            "imagen_url": "/static/productos/aceite.jpg",
        },
    )
    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["sku"] == "ACE-001"  # el SKU se normaliza a mayusculas
    assert cuerpo["stock_actual"] == 5
    assert cuerpo["activo"] is True
    assert cuerpo["imagen_url"] == "/static/productos/aceite.jpg"


def test_imagen_es_opcional(client):
    respuesta = client.post(
        "/api/v1/productos",
        json={"sku": "SAL-001", "nombre": "Sal Refisal 500 g"},
    )
    assert respuesta.status_code == 201
    assert respuesta.json()["imagen_url"] is None


def test_actualizar_imagen(client, producto):
    respuesta = client.put(
        f"/api/v1/productos/{producto['id']}",
        json={"imagen_url": "/static/productos/arroz.jpg"},
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["imagen_url"] == "/static/productos/arroz.jpg"


def test_cp02_listar_y_buscar(client, producto):
    listado = client.get("/api/v1/productos")
    assert listado.status_code == 200
    assert listado.json()["total"] == 1

    busqueda = client.get("/api/v1/productos", params={"search": "arroz"})
    assert busqueda.json()["total"] == 1

    sin_resultados = client.get("/api/v1/productos", params={"search": "zzz"})
    assert sin_resultados.json()["total"] == 0


def test_cp03_registrar_entrada(client, producto):
    respuesta = client.post(
        "/api/v1/movimientos",
        json={"producto_id": producto["id"], "tipo": "entrada", "cantidad": 20, "motivo": "compra"},
    )
    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["stock_resultante"] == 40
    assert cuerpo["movimiento"]["tipo"] == "entrada"


def test_cp04_registrar_salida(client, producto):
    respuesta = client.post(
        "/api/v1/movimientos",
        json={"producto_id": producto["id"], "tipo": "salida", "cantidad": 5, "motivo": "venta"},
    )
    assert respuesta.status_code == 201
    assert respuesta.json()["stock_resultante"] == 15

    consulta = client.get(f"/api/v1/productos/{producto['id']}")
    assert consulta.json()["stock_actual"] == 15


def test_cp05_salida_mayor_al_stock(client, producto):
    respuesta = client.post(
        "/api/v1/movimientos",
        json={"producto_id": producto["id"], "tipo": "salida", "cantidad": 999},
    )
    assert respuesta.status_code == 400
    assert "Stock insuficiente" in respuesta.json()["detail"]

    # El stock no debe haberse movido.
    consulta = client.get(f"/api/v1/productos/{producto['id']}")
    assert consulta.json()["stock_actual"] == 20


def test_cp06_cantidad_negativa(client, producto):
    respuesta = client.post(
        "/api/v1/movimientos",
        json={"producto_id": producto["id"], "tipo": "entrada", "cantidad": -5},
    )
    assert respuesta.status_code == 422


def test_cp06b_cantidad_cero(client, producto):
    respuesta = client.post(
        "/api/v1/movimientos",
        json={"producto_id": producto["id"], "tipo": "entrada", "cantidad": 0},
    )
    assert respuesta.status_code == 422


def test_cp07_producto_inexistente(client):
    respuesta = client.post(
        "/api/v1/movimientos",
        json={"producto_id": 9999, "tipo": "entrada", "cantidad": 1},
    )
    assert respuesta.status_code == 404

    consulta = client.get("/api/v1/productos/9999")
    assert consulta.status_code == 404


def test_cp08_sku_duplicado(client, producto):
    respuesta = client.post(
        "/api/v1/productos",
        json={"sku": producto["sku"], "nombre": "Otro arroz"},
    )
    assert respuesta.status_code == 409


def test_cp09_stock_consolidado_consistente(client, producto):
    client.post(
        "/api/v1/movimientos",
        json={"producto_id": producto["id"], "tipo": "entrada", "cantidad": 10},
    )
    client.post(
        "/api/v1/movimientos",
        json={"producto_id": producto["id"], "tipo": "salida", "cantidad": 7},
    )

    resumen = client.get("/api/v1/inventario/stock")
    assert resumen.status_code == 200
    datos = resumen.json()

    assert datos["total_productos"] == 1
    assert datos["items"][0]["stock_actual"] == 23  # 20 + 10 - 7
    assert datos["total_unidades"] == 23
    assert datos["items"][0]["valor"] == 23 * 3200


def test_tipo_de_movimiento_invalido(client, producto):
    respuesta = client.post(
        "/api/v1/movimientos",
        json={"producto_id": producto["id"], "tipo": "ajuste", "cantidad": 1},
    )
    assert respuesta.status_code == 422


def test_desactivar_producto(client, producto):
    respuesta = client.delete(f"/api/v1/productos/{producto['id']}")
    assert respuesta.status_code == 200
    assert respuesta.json()["activo"] is False

    # Ya no aparece en el listado ni admite movimientos.
    assert client.get("/api/v1/productos").json()["total"] == 0
    movimiento = client.post(
        "/api/v1/movimientos",
        json={"producto_id": producto["id"], "tipo": "entrada", "cantidad": 1},
    )
    assert movimiento.status_code == 400


def test_actualizar_producto(client, producto):
    respuesta = client.put(
        f"/api/v1/productos/{producto['id']}", json={"precio": 3500, "stock_minimo": 15}
    )
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["precio"] == 3500
    assert cuerpo["stock_minimo"] == 15
    assert cuerpo["nombre"] == producto["nombre"]  # lo no enviado no cambia
