import { Link } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'

export default function SiteFooter() {
  const { user, isAdmin } = useAuth()
  return (
    <footer className="border-t border-line bg-card">
      <div className="mx-auto grid max-w-6xl gap-10 px-6 py-12 md:grid-cols-4">
        <div className="md:col-span-2">
          <p className="text-sm font-semibold tracking-wide text-teal">Temperament Lab</p>
          <p className="mt-3 max-w-md text-sm leading-relaxed text-slate">
            A research platform for personality classification using classical
            data-mining algorithms. Built for education, comparison of models,
            and personal development — not clinical diagnosis.
          </p>
        </div>
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.14em] text-muted">
            Explore
          </p>
          <ul className="mt-3 space-y-2 text-sm text-slate">
            <li>
              <Link to="/#how-it-works" className="hover:text-ink">
                How it works
              </Link>
            </li>
            <li>
              <Link to="/personality-types" className="hover:text-ink">
                Personality types
              </Link>
            </li>
            <li>
              <Link to="/about" className="hover:text-ink">
                About the project
              </Link>
            </li>
          </ul>
        </div>
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.14em] text-muted">
            Account
          </p>
          <ul className="mt-3 space-y-2 text-sm text-slate">
            {user ? (
              <li>
                <Link to={isAdmin ? '/admin' : '/app'} className="hover:text-ink">
                  {isAdmin ? 'Admin console' : 'Your dashboard'}
                </Link>
              </li>
            ) : (
              <>
                <li>
                  <Link to="/login" className="hover:text-ink">
                    Login
                  </Link>
                </li>
                <li>
                  <Link to="/register" className="hover:text-ink">
                    Create account
                  </Link>
                </li>
              </>
            )}
          </ul>
        </div>
      </div>
      <div className="border-t border-line">
        <p className="mx-auto max-w-6xl px-6 py-5 text-xs leading-relaxed text-muted">
          This assessment is intended for educational, research and
          personal-development purposes and should not be considered a clinical
          psychological diagnosis.
        </p>
      </div>
    </footer>
  )
}
