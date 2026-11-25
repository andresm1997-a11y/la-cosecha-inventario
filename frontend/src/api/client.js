import axios from 'axios'

// La URL de la API se configura por entorno: en local apunta a uvicorn,
// en produccion a la URL publica de Render.
const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

const origenApi = (() => {
  try {
    return new URL(baseURL).origin
  } catch {
    return ''
  }
})()

/**
 * Convierte una ruta de imagen en URL absoluta.
 * En la base se guarda "/static/productos/arroz.jpg" para que el mismo dato
 * sirva en local y en producción; aquí se le antepone el origen de la API.
 */
export function urlImagen(ruta) {
  if (!ruta) return null
  try {
    return new URL(ruta, origenApi).href
  } catch {
    return ruta
  }
}

const api = axios.create({
  baseURL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 15000,
})

/**
 * Traduce cualquier error de la API a un mensaje legible.
 * FastAPI devuelve 422 con un arreglo de detalles por campo.
 */
export function mensajeDeError(error) {
  const detalle = error?.response?.data?.detail

  if (typeof detalle === 'string') return detalle

  if (Array.isArray(detalle)) {
    return detalle
      .map((d) => {
        const campo = Array.isArray(d.loc) ? d.loc.filter((x) => x !== 'body').join('.') : 'campo'
        return `${campo}: ${d.msg}`
      })
      .join(' · ')
  }

  if (error?.code === 'ECONNABORTED') {
    return 'La API tardó demasiado en responder. Intenta de nuevo.'
  }

  return error?.message || 'Ocurrió un error inesperado.'
}

api.interceptors.response.use(
  (respuesta) => respuesta,
  (error) => Promise.reject(new Error(mensajeDeError(error))),
)

export default api
