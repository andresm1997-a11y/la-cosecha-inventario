import { useState } from 'react'
import { urlImagen } from '../api/client'

/**
 * Miniatura del producto con respaldo: si no hay imagen o falla la carga,
 * muestra las iniciales del nombre sobre el color de la marca. Evita el
 * ícono de imagen rota y mantiene alineadas las filas de la tabla.
 */
export default function ProductoImagen({ ruta, nombre = '', tamano = 40 }) {
  const [fallo, setFallo] = useState(false)
  const src = urlImagen(ruta)

  const iniciales = nombre
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((palabra) => palabra[0])
    .join('')
    .toUpperCase()

  const estilo = { width: tamano, height: tamano }

  if (!src || fallo) {
    return (
      <div
        style={estilo}
        aria-hidden="true"
        className="flex shrink-0 items-center justify-center rounded-lg bg-verde-claro text-[11px] font-semibold text-verde-profundo"
      >
        {iniciales || '—'}
      </div>
    )
  }

  return (
    <img
      src={src}
      alt={`Imagen de ${nombre}`}
      style={estilo}
      loading="lazy"
      onError={() => setFallo(true)}
      className="shrink-0 rounded-lg border border-linea object-cover"
    />
  )
}
