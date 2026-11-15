import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import apiClient from '../../api/client'
import { useAuth } from '../../context/AuthContext'

export default function PersonalityTypesPage() {
  const { user } = useAuth()
  const [types, setTypes] = useState([])
  const [error, setError] = useState(null)
  const assessmentPath = user ? '/app/assessment' : '/register'

  useEffect(() => {
    apiClient
      .get('/personality-types')
      .then((response) => setTypes(response.data.data))
      .catch((err) => {
        setError(err.response?.data?.message || 'Could not load personality types.')
      })
  }, [])

  return (
    <main className="mx-auto max-w-6xl px-4 py-10 sm:px-6 md:py-16">
      <p className="text-sm font-medium text-teal">Educational catalogue</p>
      <h1 className="mt-2 font-serif text-3xl text-ink sm:text-4xl">Four temperament classes</h1>
      <p className="mt-3 max-w-2xl text-slate">
        Descriptions come from the database so the public site and the trained
        classifier share the same vocabulary. An assessment indicates a
        pattern; it does not diagnose a person.
      </p>
      {error && (
        <p className="mt-6 text-sm text-red-800" role="alert">
          {error}
        </p>
      )}
      <div className="mt-10 grid gap-6 md:grid-cols-2">
        {types.map((item) => (
          <article key={item.code} className="hover-lift rounded-xl border border-line bg-card p-6">
            <h2 className="font-serif text-2xl text-ink">{item.name}</h2>
            <p className="mt-2 text-sm text-teal">{item.tagline}</p>
            <p className="mt-4 text-sm leading-relaxed text-slate">{item.description}</p>
          </article>
        ))}
      </div>
      <div className="mt-12 rounded-xl border border-line bg-card px-6 py-8 text-center">
        <p className="text-slate">See which pattern your answers indicate.</p>
        <Link
          to={assessmentPath}
          className="btn-press mt-4 inline-flex rounded-full bg-teal px-5 py-2.5 text-sm font-medium text-white hover:bg-teal-dark"
        >
          Take Assessment
        </Link>
      </div>
    </main>
  )
}
