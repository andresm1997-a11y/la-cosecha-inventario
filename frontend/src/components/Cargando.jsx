export default function Cargando({ texto = 'Cargando…' }) {
  return (
    <div className="flex items-center gap-3 py-8 text-sm text-neutral-500">
      <span className="h-4 w-4 animate-spin rounded-full border-2 border-linea border-t-verde" />
      <span>{texto}</span>
    </div>
  )
}
