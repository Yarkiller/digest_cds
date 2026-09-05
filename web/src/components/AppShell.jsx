import { NavLink, Outlet } from 'react-router-dom'

const linkClass = ({ isActive }) =>
  [
    'inline-flex min-h-11 items-center rounded-full px-3 text-sm',
    isActive
      ? 'bg-accent text-accent-ink'
      : 'text-ink-2 hover:bg-paper-2',
  ].join(' ')

export default function AppShell() {
  return (
    <div className="min-h-svh bg-paper text-ink">
      <header className="border-b border-rule bg-paper">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center gap-3 px-4 py-3">
          <div className="mr-auto">
            <p className="font-display text-sm font-semibold text-accent">Digest CDS</p>
            <p className="text-xs text-muted">СВА · издание</p>
          </div>
          <nav className="flex flex-wrap gap-1" aria-label="Основная навигация">
            <NavLink to="/" end className={linkClass}>
              Выпуск
            </NavLink>
            <NavLink to="/voting" className={linkClass}>
              Голосование
            </NavLink>
            <NavLink to="/knowledge" className={linkClass}>
              База
            </NavLink>
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-4 py-10">
        <Outlet />
      </main>
    </div>
  )
}
