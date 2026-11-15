import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import AuthShell from '../../components/public/AuthShell'
import Field from '../../components/public/Field'
import { useAuth } from '../../context/AuthContext'

export default function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const [busy, setBusy] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setBusy(true)
    setError(null)
    try {
      const user = await login(email, password)
      const fallback = user.role.code === 'ADMIN' ? '/admin' : '/app'
      navigate(location.state?.from || fallback, { replace: true })
    } catch (err) {
      setError(err.response?.data?.message || 'Sign-in failed.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <AuthShell
      eyebrow="Welcome back"
      title="Sign in to continue"
      lede="Use the same account you created for assessments. Administrators are directed to the research console."
      image="/landing/auth-login.jpg"
      imageAlt="A quiet research studio with a four-colour classification display"
    >
      <h2 className="font-serif text-2xl text-ink">Login</h2>
      <p className="mt-2 text-sm text-slate">Email and password only. Roles are checked on the server.</p>
      <form className="mt-8 space-y-4" onSubmit={handleSubmit}>
        <Field
          label="Email"
          type="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          autoComplete="username"
          required
        />
        <Field
          label="Password"
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          autoComplete="current-password"
          required
        />
        {error && (
          <p className="text-sm text-red-800" role="alert">
            {error}
          </p>
        )}
        <button
          type="submit"
          disabled={busy}
          className="btn-press w-full rounded-full bg-teal py-3 text-sm font-medium text-white hover:bg-teal-dark disabled:opacity-60"
        >
          {busy ? 'Signing in…' : 'Sign in'}
        </button>
      </form>
      <p className="mt-6 text-sm text-slate">
        No account?{' '}
        <Link to="/register" className="font-medium text-teal">
          Get started
        </Link>
      </p>
    </AuthShell>
  )
}
