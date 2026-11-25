import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import Navbar from './components/Navbar'
import Movimientos from './pages/Movimientos'
import Productos from './pages/Productos'
import Stock from './pages/Stock'

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen">
        <Navbar />
        <main className="mx-auto max-w-5xl px-5 py-8 sm:px-6">
          <Routes>
            <Route path="/" element={<Navigate to="/productos" replace />} />
            <Route path="/productos" element={<Productos />} />
            <Route path="/movimientos" element={<Movimientos />} />
            <Route path="/stock" element={<Stock />} />
            <Route path="*" element={<Navigate to="/productos" replace />} />
          </Routes>
        </main>
        <footer className="mx-auto max-w-5xl px-5 pb-8 text-xs text-neutral-400 sm:px-6">
          Web y sistemas móviles · Momento 3 · Universidad Cooperativa de Colombia
        </footer>
      </div>
    </BrowserRouter>
  )
}
