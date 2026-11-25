import { NavLink } from 'react-router-dom'

const enlaces = [
  { to: '/productos', texto: 'Productos' },
  { to: '/movimientos', texto: 'Movimientos' },
  { to: '/stock', texto: 'Stock' },
]

export default function Navbar() {
  return (
    <header className="bg-verde-profundo">
      <div className="mx-auto flex max-w-5xl flex-col gap-3 px-5 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-6">
        <div>
          <p className="text-[10px] font-semibold uppercase tracking-[0.22em] text-oro">
            Distribuciones La Cosecha
          </p>
          <h1 className="text-lg font-semibold text-white">Inventario</h1>
        </div>

        <nav className="flex flex-wrap gap-1">
          {enlaces.map(({ to, texto }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `rounded-lg px-3 py-2 text-sm font-medium transition ${
                  isActive ? 'bg-white/15 text-white' : 'text-white/60 hover:text-white'
                }`
              }
            >
              {texto}
            </NavLink>
          ))}
        </nav>
      </div>
    </header>
  )
}
