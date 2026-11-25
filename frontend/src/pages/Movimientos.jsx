import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../api/client'
import Alerta from '../components/Alerta'
import Cargando from '../components/Cargando'
import { fecha, moneda } from '../formato'

export default function Movimientos() {
  const [productos, setProductos] = useState([])
  const [movimientos, setMovimientos] = useState([])
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState('')
  const [exito, setExito] = useState('')
  const [resultado, setResultado] = useState(null)
  const [enviando, setEnviando] = useState(false)
  const [form, setForm] = useState({ producto_id: '', tipo: 'entrada', cantidad: '', motivo: '' })

  async function cargarProductos() {
    const { data } = await api.get('/productos', { params: { size: 100 } })
    setProductos(data.items)
    return data.items
  }

  async function cargarMovimientos() {
    const { data } = await api.get('/movimientos', { params: { size: 10 } })
    setMovimientos(data.items)
  }

  useEffect(() => {
    let activo = true
    ;(async () => {
      try {
        await Promise.all([cargarProductos(), cargarMovimientos()])
      } catch (e) {
        if (activo) setError(e.message)
      } finally {
        if (activo) setCargando(false)
      }
    })()
    return () => {
      activo = false
    }
  }, [])

  const cambiar = (campo) => (evento) =>
    setForm((actual) => ({ ...actual, [campo]: evento.target.value }))

  async function enviar(evento) {
    evento.preventDefault()
    setEnviando(true)
    setError('')
    setExito('')
    setResultado(null)
    try {
      const cuerpo = {
        producto_id: Number(form.producto_id),
        tipo: form.tipo,
        cantidad: Number(form.cantidad),
        motivo: form.motivo.trim() || null,
      }
      const { data } = await api.post('/movimientos', cuerpo)
      setResultado(data)
      setExito(`Movimiento #${data.movimiento.id} registrado correctamente.`)
      setForm((actual) => ({ ...actual, cantidad: '', motivo: '' }))
      await Promise.all([cargarProductos(), cargarMovimientos()])
    } catch (e) {
      setError(e.message)
    } finally {
      setEnviando(false)
    }
  }

  const seleccionado = productos.find((p) => p.id === Number(form.producto_id))
  const nombreProducto = (id) =>
    productos.find((p) => p.id === id)?.nombre ?? `Producto #${id}`

  if (cargando) return <Cargando texto="Cargando movimientos…" />

  return (
    <section className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold">Movimientos</h2>
        <p className="text-sm text-neutral-500">
          Registra una entrada o una salida; el stock se actualiza en el servidor.
        </p>
      </div>

      <Alerta tipo="error" onCerrar={() => setError('')}>
        {error}
      </Alerta>
      <Alerta tipo="exito" onCerrar={() => setExito('')}>
        {exito}
      </Alerta>

      {productos.length === 0 ? (
        <div className="tarjeta p-8 text-center">
          <p className="text-sm text-neutral-500">
            Todavía no hay productos activos. Crea uno para poder registrar movimientos.
          </p>
          <Link to="/productos" className="boton mt-4">Ir a productos</Link>
        </div>
      ) : (
        <div className="grid gap-6 lg:grid-cols-3">
          <form onSubmit={enviar} className="tarjeta space-y-4 p-5 lg:col-span-1">
            <h3 className="text-sm font-semibold uppercase tracking-wide text-neutral-500">
              Registrar movimiento
            </h3>

            <div>
              <label className="etiqueta" htmlFor="producto">Producto</label>
              <select
                id="producto"
                className="campo"
                required
                value={form.producto_id}
                onChange={cambiar('producto_id')}
              >
                <option value="">Selecciona un producto</option>
                {productos.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.sku} — {p.nombre} (stock {p.stock_actual})
                  </option>
                ))}
              </select>
            </div>

            <fieldset>
              <legend className="etiqueta">Tipo</legend>
              <div className="grid grid-cols-2 gap-2">
                {['entrada', 'salida'].map((tipo) => (
                  <label
                    key={tipo}
                    className={`cursor-pointer rounded-lg border px-3 py-2 text-center text-sm font-medium capitalize transition ${
                      form.tipo === tipo
                        ? 'border-verde bg-verde-claro text-verde-profundo'
                        : 'border-linea text-neutral-500 hover:border-verde/40'
                    }`}
                  >
                    <input
                      type="radio"
                      name="tipo"
                      className="sr-only"
                      checked={form.tipo === tipo}
                      onChange={() => setForm((actual) => ({ ...actual, tipo }))}
                    />
                    {tipo}
                  </label>
                ))}
              </div>
            </fieldset>

            <div>
              <label className="etiqueta" htmlFor="cantidad">Cantidad</label>
              <input
                id="cantidad"
                type="number"
                min="1"
                step="1"
                className="campo"
                required
                placeholder="5"
                value={form.cantidad}
                onChange={cambiar('cantidad')}
              />
            </div>

            <div>
              <label className="etiqueta" htmlFor="motivo">Motivo</label>
              <input
                id="motivo"
                className="campo"
                maxLength={120}
                placeholder="venta, compra, ajuste…"
                value={form.motivo}
                onChange={cambiar('motivo')}
              />
            </div>

            {seleccionado && (
              <p className="rounded-lg bg-neutral-50 px-3 py-2 text-xs text-neutral-500">
                Stock actual de {seleccionado.sku}:{' '}
                <strong className="text-ink">{seleccionado.stock_actual}</strong> unidades
              </p>
            )}

            <button type="submit" className="boton w-full" disabled={enviando}>
              {enviando ? 'Registrando…' : 'Registrar'}
            </button>

            {resultado && (
              <p className="rounded-lg bg-verde-claro px-3 py-2 text-sm text-verde-profundo">
                Stock resultante:{' '}
                <strong>{resultado.stock_resultante}</strong> unidades
              </p>
            )}
          </form>

          <div className="tarjeta overflow-hidden lg:col-span-2">
            <div className="border-b border-linea px-5 py-4">
              <h3 className="text-sm font-semibold uppercase tracking-wide text-neutral-500">
                Últimos movimientos
              </h3>
            </div>

            {movimientos.length === 0 ? (
              <p className="p-8 text-center text-sm text-neutral-500">
                Aún no hay movimientos registrados.
              </p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-linea text-left text-[11px] uppercase tracking-wide text-neutral-500">
                      <th className="px-5 py-3 font-semibold">Fecha</th>
                      <th className="px-5 py-3 font-semibold">Producto</th>
                      <th className="px-5 py-3 font-semibold">Tipo</th>
                      <th className="px-5 py-3 font-semibold">Cantidad</th>
                      <th className="px-5 py-3 font-semibold">Motivo</th>
                    </tr>
                  </thead>
                  <tbody>
                    {movimientos.map((m) => (
                      <tr key={m.id} className="border-b border-linea/60 last:border-0">
                        <td className="whitespace-nowrap px-5 py-3 text-xs text-neutral-500">
                          {fecha(m.fecha)}
                        </td>
                        <td className="px-5 py-3">{nombreProducto(m.producto_id)}</td>
                        <td className="px-5 py-3">
                          <span
                            className={`rounded-full px-2 py-0.5 text-xs font-semibold ${
                              m.tipo === 'entrada'
                                ? 'bg-verde-claro text-verde-profundo'
                                : 'bg-oro/15 text-oro'
                            }`}
                          >
                            {m.tipo}
                          </span>
                        </td>
                        <td className="px-5 py-3 font-medium">{m.cantidad}</td>
                        <td className="px-5 py-3 text-neutral-500">{m.motivo || '—'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}
    </section>
  )
}
