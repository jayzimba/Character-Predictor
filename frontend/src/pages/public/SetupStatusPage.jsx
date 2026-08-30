import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import apiClient from '../../api/client'
import { useAuth } from '../../context/AuthContext'

const CHECKS = [
  { id: 'react', label: 'React + Vite application shell' },
  { id: 'tailwind', label: 'Tailwind CSS styling pipeline' },
  { id: 'router', label: 'Public, user and admin routes' },
  { id: 'api', label: 'Axios client talking to FastAPI' },
  { id: 'database', label: 'MySQL readiness probe' },
  { id: 'auth', label: 'JWT session in AuthContext' },
]

function StatusDot({ ok, pending }) {
  const tone = pending ? 'bg-sand' : ok ? 'bg-teal' : 'bg-red-600'
  return (
    <span
      className={`inline-block h-2.5 w-2.5 rounded-full ${tone}`}
      aria-hidden="true"
    />
  )
}

export default function SetupStatusPage() {
  const { user, login, logout, isAdmin } = useAuth()
  const [health, setHealth] = useState(null)
  const [ready, setReady] = useState(null)
  const [types, setTypes] = useState([])
  const [apiError, setApiError] = useState(null)
  const [dbError, setDbError] = useState(null)
  const [loading, setLoading] = useState(true)
  const [email, setEmail] = useState('user@temperamentlab.local')
  const [password, setPassword] = useState('DemoUser123!')
  const [authError, setAuthError] = useState(null)
  const [authBusy, setAuthBusy] = useState(false)

  useEffect(() => {
    let cancelled = false

    async function ping() {
      try {
        const healthResponse = await apiClient.get('/health')
        if (!cancelled) {
          setHealth(healthResponse.data)
          setApiError(null)
        }
      } catch (error) {
        if (!cancelled) {
          setApiError(
            error.message ||
              'Could not reach the API. Start FastAPI on port 8000.',
          )
          setLoading(false)
        }
        return
      }

      try {
        const [readyResponse, typesResponse] = await Promise.all([
          apiClient.get('/health/ready'),
          apiClient.get('/personality-types'),
        ])
        if (!cancelled) {
          setReady(readyResponse.data)
          setTypes(typesResponse.data?.data ?? [])
          setDbError(null)
        }
      } catch (error) {
        if (!cancelled) {
          setDbError(
            error.response?.data?.message ||
              'Database is unavailable. Apply migrations and start MySQL.',
          )
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    ping()
    return () => {
      cancelled = true
    }
  }, [])

  async function handleLogin(event) {
    event.preventDefault()
    setAuthBusy(true)
    setAuthError(null)
    try {
      await login(email, password)
    } catch (error) {
      setAuthError(error.response?.data?.message || 'Sign-in failed.')
    } finally {
      setAuthBusy(false)
    }
  }

  const apiOk = Boolean(health?.success)
  const dbOk = Boolean(ready?.success)

  return (
    <main className="mx-auto max-w-5xl px-6 py-16">
      <p className="text-sm font-medium text-teal">Developer status</p>
      <h1 className="mt-2 font-serif text-4xl text-ink">Environment checks</h1>
      <p className="mt-3 max-w-2xl text-slate">
        The public site now uses shared layouts and protected routes. This
        page remains at <code>/dev</code> so earlier phases can still be
        verified.
      </p>

      <section className="mt-10 grid gap-6 md:grid-cols-2">
        <article className="rounded-xl border border-line bg-card p-6">
          <h2 className="font-serif text-xl">Frontend stack</h2>
          <ul className="mt-4 space-y-3 text-sm text-slate">
            {CHECKS.map((item) => {
              const ok =
                item.id === 'database'
                  ? dbOk
                  : item.id === 'api'
                    ? apiOk
                    : item.id === 'auth'
                      ? Boolean(user)
                      : true
              const pending =
                (loading && (item.id === 'api' || item.id === 'database')) ||
                (item.id === 'auth' && authBusy)
              return (
                <li key={item.id} className="flex items-center gap-3">
                  <StatusDot ok={ok} pending={pending} />
                  <span>{item.label}</span>
                </li>
              )
            })}
          </ul>
        </article>

        <article className="rounded-xl border border-line bg-card p-6">
          <h2 className="font-serif text-xl">API and database</h2>
          {loading && <p className="mt-4 text-sm text-muted">Contacting FastAPI…</p>}
          {!loading && apiOk && (
            <dl className="mt-4 space-y-2 text-sm text-slate">
              <div className="flex justify-between gap-4">
                <dt>Process</dt>
                <dd className="font-medium text-teal">{health.data.status}</dd>
              </div>
              <div className="flex justify-between gap-4">
                <dt>MySQL</dt>
                <dd className={dbOk ? 'font-medium text-teal' : 'text-red-800'}>
                  {dbOk ? 'ready' : 'unavailable'}
                </dd>
              </div>
              {dbOk && (
                <div className="flex justify-between gap-4">
                  <dt>Questions</dt>
                  <dd>{ready.data.database.questions}</dd>
                </div>
              )}
            </dl>
          )}
          {!loading && apiError && (
            <p className="mt-4 text-sm text-red-800" role="alert">
              {apiError}
            </p>
          )}
          {!loading && dbError && (
            <p className="mt-4 text-sm text-red-800" role="alert">
              {dbError}
            </p>
          )}
        </article>
      </section>

      <section className="mt-8 rounded-xl border border-line bg-card p-6">
        <h2 className="font-serif text-xl">Session</h2>
        {user ? (
          <div className="mt-4 flex flex-wrap items-center justify-between gap-4">
            <p className="text-sm text-slate">
              Signed in as {user.first_name} {user.last_name} ({user.role.code})
            </p>
            <div className="flex gap-3 text-sm">
              <Link to={isAdmin ? '/admin' : '/app'} className="text-teal">
                Open {isAdmin ? 'admin' : 'dashboard'}
              </Link>
              <button type="button" onClick={logout} className="text-slate">
                Sign out
              </button>
            </div>
          </div>
        ) : (
          <form className="mt-4 grid gap-3 sm:grid-cols-[1fr_1fr_auto]" onSubmit={handleLogin}>
            <label className="text-sm text-slate">
              Email
              <input
                className="mt-1 w-full rounded-md border border-line bg-paper px-3 py-2"
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
              />
            </label>
            <label className="text-sm text-slate">
              Password
              <input
                className="mt-1 w-full rounded-md border border-line bg-paper px-3 py-2"
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
              />
            </label>
            <button
              type="submit"
              disabled={authBusy}
              className="self-end rounded-md bg-teal px-4 py-2 text-sm font-medium text-white"
            >
              {authBusy ? 'Signing in…' : 'Sign in'}
            </button>
          </form>
        )}
        {authError && (
          <p className="mt-3 text-sm text-red-800" role="alert">
            {authError}
          </p>
        )}
      </section>

      {types.length > 0 && (
        <p className="mt-8 text-sm text-muted">
          Catalogue loaded: {types.map((item) => item.name).join(', ')}.
        </p>
      )}
    </main>
  )
}
