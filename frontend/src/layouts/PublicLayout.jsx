import { useState } from 'react'
import { Link, NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom'
import SiteFooter from '../components/public/SiteFooter'
import { useAuth } from '../context/AuthContext'

const links = [
  { to: '/', label: 'Home', end: true },
  { to: '/#how-it-works', label: 'How It Works' },
  { to: '/personality-types', label: 'Personality Types' },
  { to: '/about', label: 'About' },
]

function navClass({ isActive }) {
  return isActive ? 'text-teal' : 'text-slate hover:text-ink'
}

export default function PublicLayout() {
  const { user, isAdmin, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [menuOpen, setMenuOpen] = useState(false)

  function closeMenu() {
    setMenuOpen(false)
  }

  return (
    <div className="flex min-h-screen flex-col bg-paper">
      <header className="sticky top-0 z-20 border-b border-line bg-card/95 backdrop-blur-sm">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-6 px-6 py-4">
          <Link to="/" className="text-sm font-semibold tracking-wide text-teal">
            Temperament Lab
          </Link>
          <nav aria-label="Primary" className="hidden items-center gap-6 text-sm md:flex">
            {links.map((link) =>
              link.to.includes('#') ? (
                <Link
                  key={link.to}
                  to={link.to}
                  className={
                    location.hash === '#how-it-works' && location.pathname === '/'
                      ? 'text-teal'
                      : 'text-slate hover:text-ink'
                  }
                >
                  {link.label}
                </Link>
              ) : (
                <NavLink key={link.to} to={link.to} end={link.end} className={navClass}>
                  {link.label}
                </NavLink>
              ),
            )}
          </nav>
          <div className="hidden items-center gap-3 text-sm md:flex">
            {user ? (
              <>
                <Link to={isAdmin ? '/admin' : '/app'} className="text-slate hover:text-ink">
                  {isAdmin ? 'Admin' : 'Dashboard'}
                </Link>
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
              </>
            ) : (
              <>
                <Link to="/login" className="text-slate hover:text-ink">
                  Login
                </Link>
                <Link
                  to="/register"
                  className="rounded-md bg-teal px-3 py-1.5 font-medium text-white hover:bg-teal-dark"
                >
                  Get Started
                </Link>
              </>
            )}
          </div>
          <button
            type="button"
            className="text-sm text-slate md:hidden"
            aria-expanded={menuOpen}
            aria-controls="mobile-nav"
            onClick={() => setMenuOpen((open) => !open)}
          >
            {menuOpen ? 'Close' : 'Menu'}
          </button>
        </div>
        {menuOpen && (
          <nav
            id="mobile-nav"
            aria-label="Mobile"
            className="space-y-3 border-t border-line px-6 py-4 text-sm md:hidden"
          >
            {links.map((link) => (
              <Link key={link.to} to={link.to} className="block text-slate" onClick={closeMenu}>
                {link.label}
              </Link>
            ))}
            {user ? (
              <Link to={isAdmin ? '/admin' : '/app'} className="block text-teal" onClick={closeMenu}>
                {isAdmin ? 'Admin' : 'Dashboard'}
              </Link>
            ) : (
              <>
                <Link to="/login" className="block text-slate" onClick={closeMenu}>
                  Login
                </Link>
                <Link to="/register" className="block text-teal" onClick={closeMenu}>
                  Get Started
                </Link>
              </>
            )}
          </nav>
        )}
      </header>
      <div className="flex-1">
        <Outlet />
      </div>
      <SiteFooter />
    </div>
  )
}
