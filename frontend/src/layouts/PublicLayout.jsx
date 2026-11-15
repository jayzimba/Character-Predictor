import { useEffect, useState } from 'react'
import { Link, NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom'
import BrandLogo from '../components/BrandLogo'
import PageFade from '../components/PageFade'
import SkipLink from '../components/SkipLink'
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

  useEffect(() => {
    setMenuOpen(false)
  }, [location.pathname, location.hash])

  function closeMenu() {
    setMenuOpen(false)
  }

  return (
    <div className="flex min-h-screen flex-col bg-paper">
      <SkipLink />
      <header className="sticky top-0 z-20 border-b border-line/70 bg-card/80 backdrop-blur-md">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-3 sm:px-6 sm:py-4">
          <Link to="/" className="rounded-md" aria-label="Temperament Lab home">
            <BrandLogo />
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
                  className="btn-press rounded-full bg-teal px-4 py-2 font-medium text-white hover:bg-teal-dark"
                >
                  Get Started
                </Link>
              </>
            )}
          </div>
          <button
            type="button"
            className="rounded-md px-3 py-2 text-sm text-slate hover:bg-sand hover:text-ink md:hidden"
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
            className="animate-menu space-y-1 border-t border-line px-4 py-3 text-sm md:hidden"
          >
            {links.map((link) => (
              <Link
                key={link.to}
                to={link.to}
                className="block rounded-md px-2 py-2.5 text-slate hover:bg-sand"
                onClick={closeMenu}
              >
                {link.label}
              </Link>
            ))}
            {user ? (
              <>
                <Link
                  to={isAdmin ? '/admin' : '/app'}
                  className="block rounded-md px-2 py-2.5 text-teal hover:bg-sand"
                  onClick={closeMenu}
                >
                  {isAdmin ? 'Admin' : 'Dashboard'}
                </Link>
                <button
                  type="button"
                  className="block w-full rounded-md px-2 py-2.5 text-left text-slate hover:bg-sand"
                  onClick={() => {
                    closeMenu()
                    logout()
                    navigate('/')
                  }}
                >
                  Sign out
                </button>
              </>
            ) : (
              <>
                <Link
                  to="/login"
                  className="block rounded-md px-2 py-2.5 text-slate hover:bg-sand"
                  onClick={closeMenu}
                >
                  Login
                </Link>
                <Link
                  to="/register"
                  className="block rounded-md px-2 py-2.5 text-teal hover:bg-sand"
                  onClick={closeMenu}
                >
                  Get Started
                </Link>
              </>
            )}
          </nav>
        )}
      </header>
      <div id="main-content" className="flex flex-1 flex-col">
        <PageFade>
          <Outlet />
        </PageFade>
      </div>
      <SiteFooter />
    </div>
  )
}
