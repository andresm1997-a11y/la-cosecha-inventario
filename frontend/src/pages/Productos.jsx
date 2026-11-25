import { useEffect, useState } from 'react'
import api from '../api/client'
import Alerta from '../components/Alerta'
import Cargando from '../components/Cargando'
import ProductoImagen from '../components/ProductoImagen'
import { moneda } from '../formato'

const VACIO = {
  sku: '',
  nombre: '',
  categoria: '',
  imagen_url: '',
  precio: '',
  stock_actual: '',
  stock_minimo: '',
}

export default function Productos() {
  const [productos, setProductos] = useState([])
  const [total, setTotal] = useState(0)
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState('')
  const [exito, setExito] = useState('')
  const [busqueda, setBusqueda] = useState('')
  const [form, setForm] = useState(VACIO)
  const [enviando, setEnviando] = useState(false)

  async function cargar(texto = '') {
    setCargando(true)
    setError('')
    try {
      const { data } = await api.get('/productos', {
        params: { search: texto.trim() || undefined, size: 50 },
      })
      setProductos(data.items)
      setTotal(data.total)
    } catch (e) {
      setError(e.message)
    } finally {
      setCargando(false)
    }
  }

  useEffect(() => {
    cargar()
  }, [])

  const cambiar = (campo) => (evento) =>
    setForm((actual) => ({ ...actual, [campo]: evento.target.value }))

  async function buscar(evento) {
    evento.preventDefault()
    await cargar(busqueda)
  }

  async function limpiar() {
    setBusqueda('')
    await cargar('')
  }

  async function enviar(evento) {
    evento.preventDefault()
    setEnviando(true)
    setError('')
    setExito('')
    try {
      const nuevo = {
        sku: form.sku.trim(),
        nombre: form.nombre.trim(),
        categoria: form.categoria.trim() || null,
        imagen_url: form.imagen_url.trim() || null,
        precio: form.precio === '' ? 0 : Number(form.precio),
        stock_actual: form.stock_actual === '' ? 0 : Number(form.stock_actual),
        stock_minimo: form.stock_minimo === '' ? 0 : Number(form.stock_minimo),
      }
      await api.post('/productos', nuevo)
      setForm(VACIO)
      setExito(`Producto ${nuevo.sku.toUpperCase()} creado correctamente.`)
      await cargar(busqueda)
    } catch (e) {
      setError(e.message)
    } finally {
      setEnviando(false)
    }
  }

  return (
    <section className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h2 className="text-2xl font-semibold">Productos</h2>
          <p className="text-sm text-neutral-500">
            {total} {total === 1 ? 'producto activo' : 'productos activos'} en el catálogo
          </p>
        </div>

        <form onSubmit={buscar} className="flex gap-2">
          <input
            className="campo sm:w-64"
            placeholder="Buscar por nombre o SKU"
            value={busqueda}
            onChange={(evento) => setBusqueda(evento.target.value)}
            aria-label="Buscar productos"
          />
          <button type="submit" className="boton-secundario">
            Buscar
          </button>
          {busqueda && (
            <button type="button" onClick={limpiar} className="text-xs font-semibold text-neutral-500">
              Limpiar
            </button>
          )}
        </form>
      </div>

      <Alerta tipo="error" onCerrar={() => setError('')}>
        {error}
      </Alerta>
      <Alerta tipo="exito" onCerrar={() => setExito('')}>
        {exito}
      </Alerta>

      <div className="grid gap-6 lg:grid-cols-3">
        <form onSubmit={enviar} className="tarjeta space-y-4 p-5 lg:col-span-1">
          <h3 className="text-sm font-semibold uppercase tracking-wide text-neutral-500">
            Nuevo producto
          </h3>

          <div>
            <label className="etiqueta" htmlFor="sku">SKU</label>
            <input id="sku" className="campo" required maxLength={40}
              placeholder="ARR-001" value={form.sku} onChange={cambiar('sku')} />
          </div>

          <div>
            <label className="etiqueta" htmlFor="nombre">Nombre</label>
            <input id="nombre" className="campo" required maxLength={120}
              placeholder="Arroz Diana 500 g" value={form.nombre} onChange={cambiar('nombre')} />
          </div>

          <div>
            <label className="etiqueta" htmlFor="categoria">Categoría</label>
            <input id="categoria" className="campo" maxLength={60}
              placeholder="Granos" value={form.categoria} onChange={cambiar('categoria')} />
          </div>

          <div>
            <label className="etiqueta" htmlFor="imagen_url">Imagen (ruta o URL)</label>
            <input id="imagen_url" className="campo" maxLength={255}
              placeholder="/static/productos/arroz.jpg"
              value={form.imagen_url} onChange={cambiar('imagen_url')} />
            <div className="mt-2 flex items-center gap-2">
              <ProductoImagen ruta={form.imagen_url} nombre={form.nombre} tamano={36} />
              <span className="text-[11px] text-neutral-400">
                {form.imagen_url ? 'Vista previa' : 'Sin imagen: se muestran las iniciales'}
              </span>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="etiqueta" htmlFor="precio">Precio</label>
              <input id="precio" type="number" min="0" step="1" className="campo"
                placeholder="3200" value={form.precio} onChange={cambiar('precio')} />
            </div>
            <div>
              <label className="etiqueta" htmlFor="stock_minimo">Stock mínimo</label>
              <input id="stock_minimo" type="number" min="0" step="1" className="campo"
                placeholder="10" value={form.stock_minimo} onChange={cambiar('stock_minimo')} />
            </div>
          </div>

          <div>
            <label className="etiqueta" htmlFor="stock_actual">Stock inicial</label>
            <input id="stock_actual" type="number" min="0" step="1" className="campo"
              placeholder="0" value={form.stock_actual} onChange={cambiar('stock_actual')} />
          </div>

          <button type="submit" className="boton w-full" disabled={enviando}>
            {enviando ? 'Guardando…' : 'Crear producto'}
          </button>
        </form>

        <div className="tarjeta overflow-hidden lg:col-span-2">
          {cargando ? (
            <Cargando texto="Cargando productos…" />
          ) : productos.length === 0 ? (
            <p className="p-8 text-center text-sm text-neutral-500">
              No hay productos que coincidan. Crea el primero con el formulario.
            </p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-linea text-left text-[11px] uppercase tracking-wide text-neutral-500">
                    <th className="px-5 py-3 font-semibold">SKU</th>
                    <th className="px-5 py-3 font-semibold">Producto</th>
                    <th className="px-5 py-3 font-semibold">Precio</th>
                    <th className="px-5 py-3 font-semibold">Stock</th>
                  </tr>
                </thead>
                <tbody>
                  {productos.map((p) => {
                    const bajo = p.stock_actual <= p.stock_minimo
                    return (
                      <tr key={p.id} className="border-b border-linea/60 last:border-0">
                        <td className="px-5 py-2 align-middle font-mono text-xs text-neutral-500">
                          {p.sku}
                        </td>
                        <td className="px-5 py-2 align-middle">
                          <div className="flex items-center gap-3">
                            <ProductoImagen ruta={p.imagen_url} nombre={p.nombre} tamano={40} />
                            <div className="min-w-0">
                              <p className="truncate font-medium">{p.nombre}</p>
                              {p.categoria && (
                                <p className="text-[11px] text-neutral-400">{p.categoria}</p>
                              )}
                            </div>
                          </div>
                        </td>
                        <td className="px-5 py-2 align-middle text-neutral-600">{moneda(p.precio)}</td>
                        <td className="px-5 py-2 align-middle">
                          <span
                            className={`rounded-full px-2.5 py-1 text-xs font-semibold ${
                              bajo ? 'bg-oro/15 text-oro' : 'bg-verde-claro text-verde-profundo'
                            }`}
                          >
                            {p.stock_actual}
                          </span>
                          <span className="ml-2 text-xs text-neutral-400">mín. {p.stock_minimo}</span>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </section>
  )
}
