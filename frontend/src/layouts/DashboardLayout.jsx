import { useEffect, useState } from 'react'
import { Link, NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom'
import BrandLogo from '../components/BrandLogo'
import PageFade from '../components/PageFade'
import SkipLink from '../components/SkipLink'
import { useAuth } from '../context/AuthContext'

function itemClass({ isActive }) {
  return `block rounded-md px-3 py-2.5 text-sm md:py-2 ${
    isActive ? 'bg-sand text-ink' : 'text-slate hover:bg-paper hover:text-ink'
  }`
}

export default function DashboardLayout({ variant }) {
  const { user, isAdmin, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [menuOpen, setMenuOpen] = useState(false)
  const isAdminShell = variant === 'admin'

  useEffect(() => {
    setMenuOpen(false)
  }, [location.pathname])

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
        { to: '/admin/audit', label: 'Audit log' },
      ]
    : [
        { to: '/app', label: 'Dashboard', end: true },
        { to: '/app/assessment', label: 'Take assessment' },
        { to: '/app/results', label: 'Results' },
        { to: '/app/history', label: 'History' },
        { to: '/app/profile', label: 'Profile' },
      ]

  return (
    <div className="min-h-screen bg-paper md:grid md:grid-cols-[16rem_minmax(0,1fr)] print:block print:bg-white">
      <SkipLink />
      <div className="sticky top-0 z-30 flex items-center justify-between border-b border-line bg-card px-4 py-3 md:hidden print:hidden">
        <Link to="/" className="rounded-md" aria-label="Temperament Lab home">
          <BrandLogo />
        </Link>
        <button
          type="button"
          className="rounded-md px-3 py-2 text-sm text-slate hover:bg-sand hover:text-ink"
          aria-expanded={menuOpen}
          aria-controls="dashboard-nav"
          onClick={() => setMenuOpen((open) => !open)}
        >
          {menuOpen ? 'Close' : 'Menu'}
        </button>
      </div>
      <aside
        className={`${
          menuOpen ? 'block' : 'hidden'
        } border-b border-line bg-card md:sticky md:top-0 md:flex md:h-screen md:flex-col md:border-b-0 md:border-r print:hidden`}
      >
        <div className="hidden px-5 py-4 md:block">
          <Link to="/" className="rounded-md" aria-label="Temperament Lab home">
            <BrandLogo />
          </Link>
          <p className="mt-1 text-xs uppercase tracking-[0.14em] text-muted">
            {isAdminShell ? 'Administration' : 'Workspace'}
          </p>
        </div>
        <nav
          id="dashboard-nav"
          aria-label={isAdminShell ? 'Admin' : 'User'}
          className="space-y-1 px-3 py-3 md:flex-1 md:overflow-y-auto"
        >
          {links.map((link) => (
            <NavLink key={link.to} to={link.to} end={link.end} className={itemClass}>
              {link.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <div className="flex min-w-0 flex-col">
        <header className="flex items-center justify-between gap-3 border-b border-line bg-card px-4 py-3 sm:px-6 print:hidden">
          <p className="min-w-0 truncate text-sm text-slate">
            {user.first_name} {user.last_name}
            <span className="ml-2 text-xs uppercase tracking-wide text-muted">
              {user.role.code}
            </span>
          </p>
          <div className="flex shrink-0 items-center gap-3 text-sm sm:gap-4">
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
        <main id="main-content" className="w-full min-w-0 px-4 py-6 sm:px-6 lg:px-8 lg:py-8">
          <PageFade>
            <Outlet />
          </PageFade>
        </main>
      </div>
    </div>
  )
}
