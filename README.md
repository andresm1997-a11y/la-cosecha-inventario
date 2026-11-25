# Inventario La Cosecha

Sistema de gestión de inventarios para **Distribuciones La Cosecha S.A.S.**, una
microempresa de abarrotes con cerca de 1.200 referencias. Resuelve el problema
central del negocio: hoy el inventario vive en Excel, un cuaderno de bodega y
WhatsApp, y esas tres fuentes casi nunca coinciden.

Este repositorio es el proyecto integrador del curso **Web y sistemas móviles**
(Momento evaluativo #3) de la Universidad Cooperativa de Colombia.

- **Aplicación:** https://la-cosecha-inventario.vercel.app
- **API:** https://inventario-api-aixi.onrender.com
- **Documentación de la API:** https://inventario-api-aixi.onrender.com/docs

> Los servicios gratuitos se suspenden por inactividad: la primera petición
> puede tardar hasta un minuto en responder.

## Qué hace

- Catálogo de productos con búsqueda por nombre o SKU, control de stock mínimo e
  imagen por producto.
- Registro de entradas y salidas de inventario.
- Actualización del stock en el servidor, dentro de la misma transacción que
  guarda el movimiento.
- Tablero con el stock consolidado, el valor del inventario y las referencias
  que requieren reposición.

## Arquitectura

Arquitectura cliente–servidor de tres capas, con tres despliegues independientes:

| Capa | Tecnología | Dónde vive |
|---|---|---|
| Presentación | React 18 + Vite + Tailwind CSS | Netlify o Vercel |
| Aplicación | FastAPI + SQLAlchemy + Pydantic | Render o Railway |
| Datos | PostgreSQL (SQLite en desarrollo) | Render |

El cliente nunca accede a la base de datos: toda operación pasa por la API, y las
reglas de negocio se validan en el servidor.

## Estructura

```
backend/
  app/
    main.py          instancia FastAPI, CORS y routers
    database.py      engine, sesión y Base de SQLAlchemy
    models.py        Producto y Movimiento
    schemas.py       validaciones con Pydantic
    routers/         productos, movimientos, inventario
  tests/test_api.py  15 pruebas con pytest
  static/productos/  imágenes del catálogo (servidas en /static)
  requirements.txt
  .env.example
frontend/
  src/
    api/client.js    instancia de axios con VITE_API_URL y urlImagen()
    pages/           Productos, Movimientos, Stock
    components/      Alerta, Cargando, Navbar, ProductoImagen
  .env.example
docs/
  capturas/          evidencia del sistema en funcionamiento
README.md
```

## Cómo ejecutarlo en local

### 1. Backend

```bash
cd backend
python -m venv .venv
# Windows:  .venv\Scripts\activate
# Linux/macOS:  source .venv/bin/activate
pip install -r requirements-dev.txt
python seed.py                 # carga el catálogo de ejemplo
uvicorn app.main:app --reload --port 8000
```

La documentación interactiva queda en <http://localhost:8000/docs>.
Si no se define `DATABASE_URL`, se usa SQLite (`backend/inventario.db`).

### 2. Frontend

```bash
cd frontend
npm install
cp .env.example .env           # en Windows: copy .env.example .env
npm run dev
```

La aplicación queda en <http://localhost:5173>.

### Variables de entorno

| Archivo | Variable | Para qué sirve |
|---|---|---|
| `backend/.env` | `DATABASE_URL` | Cadena de conexión (SQLite en local, PostgreSQL en producción) |
| `backend/.env` | `ALLOWED_ORIGINS` | Dominios autorizados por CORS, separados por coma |
| `frontend/.env` | `VITE_API_URL` | URL base de la API, incluyendo `/api/v1` |

## Pruebas

```bash
cd backend
python -m pytest -v
```

15 pruebas que cubren los casos del informe: creación de productos, búsqueda,
entradas, salidas, stock insuficiente, cantidades inválidas, producto
inexistente, SKU duplicado y consistencia del stock consolidado. Además se
verifica que la imagen sea opcional y que se pueda actualizar.

## Imágenes de producto

Cada producto puede llevar una imagen. El archivo vive en
`backend/static/productos/` y la API lo publica en `/static`; la base de datos
guarda **solo la ruta relativa** (`/static/productos/arroz.jpg`).

Esa decisión evita tener que reescribir datos al cambiar de entorno: el frontend
resuelve la ruta contra el origen de `VITE_API_URL` con el helper `urlImagen()`.
En local la imagen sale de `http://localhost:8000` y en producción de la URL de
Render, sin tocar la base.

Si un producto no tiene imagen o la imagen falla, el componente `ProductoImagen`
muestra las iniciales del nombre en lugar del ícono de imagen rota.

Para agregar una imagen: copiar el archivo a `backend/static/productos/` y
registrar la ruta en el campo `imagen_url` del producto (desde el formulario o
con `PUT /api/v1/productos/{id}`).

Atribución y licencias de las imágenes incluidas: ver [CREDITOS.md](CREDITOS.md).

## API

| Método | Ruta | Función |
|---|---|---|
| GET | `/api/v1/productos` | Listar con búsqueda y paginación |
| GET | `/api/v1/productos/{id}` | Consultar un producto |
| POST | `/api/v1/productos` | Crear producto |
| PUT | `/api/v1/productos/{id}` | Actualizar producto |
| DELETE | `/api/v1/productos/{id}` | Desactivar producto |
| POST | `/api/v1/movimientos` | Registrar entrada o salida |
| GET | `/api/v1/movimientos` | Listar con filtros por producto y fecha |
| GET | `/api/v1/inventario/stock` | Stock consolidado y totales |

Reglas de negocio: la cantidad debe ser mayor que cero (422), una salida no
puede superar el stock disponible (400), el producto debe existir (404) y el SKU
es único (409).

## Despliegue

**Backend en Render**

- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Variables: `DATABASE_URL` (cadena interna de PostgreSQL) y `ALLOWED_ORIGINS`

**Frontend en Netlify**

- Build command: `npm run build`
- Publish directory: `dist`
- Variable: `VITE_API_URL` con la URL de Render terminada en `/api/v1`
- El archivo `public/_redirects` resuelve las rutas de React Router

## Capturas

En `docs/capturas/`: catálogo de productos, registro de movimientos, tablero de
stock, confirmación de una entrada y rechazo de una salida sin stock.

## Alcance y trabajo futuro

El MVP cubre catálogo, movimientos, stock y validaciones. Quedan por fuera, de
forma deliberada: escaneo de código de barras, modo offline, autenticación con
JWT y roles, alertas de vencimiento y reportes de valor por periodo.

## Autor

Andrés Camilo Montaño Quintero — Ingeniería en Sistemas, Universidad Cooperativa
de Colombia. Curso: Web y sistemas móviles. Docente: Oscar Barragán Páez.
