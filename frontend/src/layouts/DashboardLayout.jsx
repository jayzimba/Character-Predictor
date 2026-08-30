import { Link, NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

function itemClass({ isActive }) {
  return `block rounded-md px-3 py-2 text-sm ${
    isActive ? 'bg-sand text-ink' : 'text-slate hover:bg-paper hover:text-ink'
  }`
}

export default function DashboardLayout({ variant }) {
  const { user, isAdmin, logout } = useAuth()
  const navigate = useNavigate()
  const isAdminShell = variant === 'admin'

  const links = isAdminShell
    ? [
        { to: '/admin', label: 'Overview', end: true },
        { to: '/admin/users', label: 'Users' },
        { to: '/admin/questions', label: 'Questions' },
        { to: '/admin/assessments', label: 'Assessments' },
        { to: '/admin/models', label: 'Models' },
        { to: '/admin/dataset', label: 'Dataset' },
        { to: '/admin/training', label: 'Training' },
        { to: '/admin/analytics', label: 'Analytics' },
      ]
    : [
        { to: '/app', label: 'Dashboard', end: true },
        { to: '/app/assessment', label: 'Take assessment' },
        { to: '/app/history', label: 'History' },
        { to: '/app/profile', label: 'Profile' },
      ]

  return (
    <div className="min-h-screen bg-paper md:grid md:grid-cols-[240px_1fr]">
      <aside className="border-b border-line bg-card md:min-h-screen md:border-b-0 md:border-r">
        <div className="flex items-center justify-between px-5 py-4 md:block">
          <Link to="/" className="text-sm font-semibold tracking-wide text-teal">
            Temperament Lab
          </Link>
          <p className="mt-1 hidden text-xs uppercase tracking-[0.14em] text-muted md:block">
            {isAdminShell ? 'Administration' : 'Workspace'}
          </p>
        </div>
        <nav aria-label={isAdminShell ? 'Admin' : 'User'} className="flex gap-1 overflow-x-auto px-3 pb-3 md:block md:space-y-1">
          {links.map((link) => (
            <NavLink key={link.to} to={link.to} end={link.end} className={itemClass}>
              {link.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <div>
        <header className="flex items-center justify-between border-b border-line bg-card px-6 py-3">
          <p className="text-sm text-slate">
            {user.first_name} {user.last_name}
            <span className="ml-2 text-xs uppercase tracking-wide text-muted">
              {user.role.code}
            </span>
          </p>
          <div className="flex items-center gap-4 text-sm">
            {isAdmin && !isAdminShell && (
              <Link to="/admin" className="text-teal">
                Admin
              </Link>
            )}
            {isAdminShell && (
              <Link to="/app" className="text-teal">
                User app
              </Link>
            )}
            <button
              type="button"
              onClick={() => {
                logout()
                navigate('/')
              }}
              className="text-slate hover:text-ink"
            >
              Sign out
            </button>
          </div>
        </header>
        <main className="px-6 py-8">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
