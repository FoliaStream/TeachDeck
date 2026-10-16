import {
  Routes,
  Route,
  NavLink,
  Navigate,
  Outlet,
} from 'react-router-dom'

import TablePage from './pages/TablePage'

import './App.css'

// Shared frame of every page: title, menu, and the place where the current page appears
function Layout() {
  return (
    <div className="layout">
      <header className="nav">
        <h1>TeachDeck</h1>
        <nav>
          <NavLink to="/tables">Tables</NavLink>
        </nav>
      </header>
      <main>
        <Outlet />
      </main>
    </div>
  )
}

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Navigate to="/tables" replace />} />
        <Route path="tables" element={<TablePage />} />
        <Route path="*" element={<Navigate to="/tables" replace />} />
      </Route>
    </Routes>
  )
}