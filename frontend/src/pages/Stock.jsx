import { useEffect, useState } from 'react'
import api from '../api/client'
import Alerta from '../components/Alerta'
import Cargando from '../components/Cargando'
import ProductoImagen from '../components/ProductoImagen'
import { moneda } from '../formato'

function Indicador({ etiqueta, valor, detalle, acento }) {
  return (
    <div className="tarjeta p-5">
      <p className="text-[11px] font-semibold uppercase tracking-wide text-neutral-500">
        {etiqueta}
      </p>
      <p className={`mt-2 text-2xl font-semibold ${acento || ''}`}>{valor}</p>
      {detalle && <p className="mt-1 text-xs text-neutral-400">{detalle}</p>}
    </div>
  )
}

export default function Stock() {
  const [resumen, setResumen] = useState(null)
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState('')
  const [actualizado, setActualizado] = useState('')

  async function cargar() {
    setCargando(true)
    setError('')
    try {
      const { data } = await api.get('/inventario/stock')
      setResumen(data)
      setActualizado(new Date().toLocaleTimeString('es-CO'))
    } catch (e) {
      setError(e.message)
    } finally {
      setCargando(false)
    }
  }

  useEffect(() => {
    cargar()
  }, [])

  return (
    <section className="space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h2 className="text-2xl font-semibold">Stock</h2>
          <p className="text-sm text-neutral-500">
            Consolidado del inventario calculado en el servidor.
          </p>
        </div>
        <div className="flex items-center gap-3">
          {actualizado && (
            <span className="text-xs text-neutral-400">Actualizado {actualizado}</span>
          )}
          <button type="button" onClick={cargar} className="boton-secundario">
            Actualizar
          </button>
        </div>
      </div>

      <Alerta tipo="error" onCerrar={() => setError('')}>
        {error}
      </Alerta>

      {cargando && !resumen ? (
        <Cargando texto="Consultando el inventario…" />
      ) : (
        resumen && (
          <>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <Indicador
                etiqueta="Productos activos"
                valor={resumen.total_productos}
                detalle="Referencias en el catálogo"
              />
              <Indicador
                etiqueta="Unidades en bodega"
                valor={resumen.total_unidades}
                detalle="Suma del stock actual"
              />
              <Indicador
                etiqueta="Valor del inventario"
                valor={moneda(resumen.valor_total)}
                detalle="Precio por unidad en stock"
              />
              <Indicador
                etiqueta="Bajo stock"
                valor={resumen.productos_bajo_stock}
                detalle="Requieren reposición"
                acento={resumen.productos_bajo_stock > 0 ? 'text-oro' : 'text-verde'}
              />
            </div>

            <div className="tarjeta overflow-hidden">
              {resumen.items.length === 0 ? (
                <p className="p-8 text-center text-sm text-neutral-500">
                  No hay productos activos todavía.
                </p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-linea text-left text-[11px] uppercase tracking-wide text-neutral-500">
                        <th className="px-5 py-3 font-semibold">SKU</th>
                        <th className="px-5 py-3 font-semibold">Producto</th>
                        <th className="px-5 py-3 font-semibold">Stock</th>
                        <th className="px-5 py-3 font-semibold">Mínimo</th>
                        <th className="px-5 py-3 font-semibold">Valor</th>
                        <th className="px-5 py-3 font-semibold">Estado</th>
                      </tr>
                    </thead>
                    <tbody>
                      {resumen.items.map((item) => (
                        <tr key={item.id} className="border-b border-linea/60 last:border-0">
                          <td className="px-5 py-2 align-middle font-mono text-xs text-neutral-500">
                            {item.sku}
                          </td>
                          <td className="px-5 py-2 align-middle">
                            <div className="flex items-center gap-3">
                              <ProductoImagen
                                ruta={item.imagen_url}
                                nombre={item.nombre}
                                tamano={40}
                              />
                              <div className="min-w-0">
                                <p className="truncate font-medium">{item.nombre}</p>
                                {item.categoria && (
                                  <p className="text-[11px] text-neutral-400">{item.categoria}</p>
                                )}
                              </div>
                            </div>
                          </td>
                          <td className="px-5 py-2 align-middle font-semibold">{item.stock_actual}</td>
                          <td className="px-5 py-2 align-middle text-neutral-500">{item.stock_minimo}</td>
                          <td className="px-5 py-2 align-middle text-neutral-600">{moneda(item.valor)}</td>
                          <td className="px-5 py-2 align-middle">
                            <span
                              className={`rounded-full px-2.5 py-1 text-xs font-semibold ${
                                item.stock_bajo
                                  ? 'bg-oro/15 text-oro'
                                  : 'bg-verde-claro text-verde-profundo'
                              }`}
                            >
                              {item.stock_bajo ? 'Reponer' : 'Disponible'}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </>
        )
      )}
    </section>
  )
}
