const estilos = {
  exito: 'border-verde/30 bg-verde-claro text-verde-profundo',
  error: 'border-red-200 bg-red-50 text-red-800',
  info: 'border-linea bg-white text-neutral-600',
}

export default function Alerta({ tipo = 'info', children, onCerrar }) {
  if (!children) return null

  return (
    <div
      role={tipo === 'error' ? 'alert' : 'status'}
      className={`mb-4 flex items-start justify-between gap-4 rounded-lg border px-4 py-3 text-sm ${estilos[tipo]}`}
    >
      <span>{children}</span>
      {onCerrar && (
        <button
          type="button"
          onClick={onCerrar}
          className="shrink-0 text-[11px] font-semibold uppercase tracking-wide opacity-60 transition hover:opacity-100"
        >
          Cerrar
        </button>
      )}
    </div>
  )
}
