import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import AuthShell from '../../components/public/AuthShell'
import Field, { selectClass } from '../../components/public/Field'
import { useAuth } from '../../context/AuthContext'

const emptyForm = {
  first_name: '',
  last_name: '',
  email: '',
  password: '',
  confirm_password: '',
  gender: '',
  age_group: '',
}

function formatErrors(details) {
  const items = details?.errors
  if (!Array.isArray(items) || items.length === 0) {
    return details?.message || 'Registration failed.'
  }
  return items
    .map((item) => item.message || item)
    .filter(Boolean)
    .join(' ')
}

export default function RegisterPage() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState(emptyForm)
  const [error, setError] = useState(null)
  const [busy, setBusy] = useState(false)

  function update(field) {
    return (event) => setForm((current) => ({ ...current, [field]: event.target.value }))
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setBusy(true)
    setError(null)
    try {
      const payload = {
        ...form,
        gender: form.gender || null,
        age_group: form.age_group || null,
      }
      await register(payload)
      navigate('/app', { replace: true })
    } catch (err) {
      setError(formatErrors(err.response?.data))
    } finally {
      setBusy(false)
    }
  }

  return (
    <AuthShell
      eyebrow="Create an account"
      title="Start with a short profile"
      lede="New accounts always receive the USER role. Administrators are created separately for the research console."
    >
      <h2 className="font-serif text-2xl text-ink">Get started</h2>
      <p className="mt-2 text-sm text-slate">
        Password must be at least eight characters and include a letter and a number.
      </p>
      <form className="mt-8 space-y-4" onSubmit={handleSubmit}>
        <div className="grid gap-4 sm:grid-cols-2">
          <Field label="First name" value={form.first_name} onChange={update('first_name')} required />
          <Field label="Last name" value={form.last_name} onChange={update('last_name')} required />
        </div>
        <Field
          label="Email"
          type="email"
          value={form.email}
          onChange={update('email')}
          autoComplete="email"
          required
        />
        <Field
          label="Password"
          type="password"
          value={form.password}
          onChange={update('password')}
          autoComplete="new-password"
          required
        />
        <Field
          label="Confirm password"
          type="password"
          value={form.confirm_password}
          onChange={update('confirm_password')}
          autoComplete="new-password"
          required
        />
        <Field label="Gender (optional)">
          <select className={selectClass} value={form.gender} onChange={update('gender')}>
            <option value="">Prefer not to say</option>
            <option value="FEMALE">Female</option>
            <option value="MALE">Male</option>
            <option value="OTHER">Other</option>
            <option value="PREFER_NOT_TO_SAY">Prefer not to say</option>
          </select>
        </Field>
        <Field label="Age group (optional)">
          <select className={selectClass} value={form.age_group} onChange={update('age_group')}>
            <option value="">Prefer not to say</option>
            <option value="UNDER_18">Under 18</option>
            <option value="AGE_18_24">18–24</option>
            <option value="AGE_25_34">25–34</option>
            <option value="AGE_35_44">35–44</option>
            <option value="AGE_45_54">45–54</option>
            <option value="AGE_55_PLUS">55+</option>
          </select>
        </Field>
        {error && (
          <p className="text-sm text-red-800" role="alert">
            {error}
          </p>
        )}
        <button
          type="submit"
          disabled={busy}
          className="w-full rounded-md bg-teal py-2.5 text-sm font-medium text-white hover:bg-teal-dark disabled:opacity-60"
        >
          {busy ? 'Creating account…' : 'Create account'}
        </button>
      </form>
      <p className="mt-6 text-sm text-slate">
        Already registered?{' '}
        <Link to="/login" className="font-medium text-teal">
          Sign in
        </Link>
      </p>
    </AuthShell>
  )
}
