import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { fetchAdminOverview } from '../../api/admin'
import StatCard from '../../components/dashboard/StatCard'

const TYPES = [
  { key: 'choleric', name: 'Choleric', color: '#c45c26' },
  { key: 'melancholic', name: 'Melancholic', color: '#3d4f66' },
  { key: 'phlegmatic', name: 'Phlegmatic', color: '#0f6e68' },
  { key: 'sanguine', name: 'Sanguine', color: '#b0893e' },
]

export default function AdminDashboardPage() {
  const [summary, setSummary] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchAdminOverview()
      .then((response) => setSummary(response.data.data))
      .catch((err) => {
        setError(err.response?.data?.message || 'Could not load the admin overview.')
      })
  }, [])

  const counts = summary?.personality_counts
  const classified = summary?.classifications_stored ?? 0
  const maxCount = counts ? Math.max(...Object.values(counts), 1) : 1
  const active = summary?.active_model

  return (
    <div>
      <p className="text-sm font-medium text-teal">Administration</p>
      <h1 className="mt-1 font-serif text-2xl text-ink sm:text-3xl">Overview</h1>
      <p className="mt-2 max-w-2xl text-slate">
        Totals come from MySQL. The type distribution is a count of stored
        classifications, not a new prediction.
      </p>

      {error && (
        <p className="mt-6 text-sm text-red-800" role="alert">
          {error}
        </p>
      )}

      <section className="mt-8 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label="Registered users"
          value={summary ? summary.users_total : '—'}
          hint={
            summary
              ? `${summary.users_regular} participants · ${summary.users_admin} admins`
              : 'Accounts in the database'
          }
        />
        <StatCard
          label="Assessments completed"
          value={summary ? summary.assessments_completed : '—'}
          hint={
            summary?.assessments_in_progress
              ? `${summary.assessments_in_progress} in progress`
              : 'Finished submissions only'
          }
        />
        <StatCard
          label="Stored classifications"
          value={summary ? summary.classifications_stored : '—'}
          hint={
            summary?.demo_classifications
              ? `${summary.demo_classifications} in DEMO MODE`
              : 'Predictions already saved'
          }
        />
        <StatCard
          label="Active model"
          value={
            active ? active.algorithm.replaceAll('_', ' ') : 'None'
          }
          hint={
            active
              ? `${active.version}${active.is_synthetic_dataset ? ' · DEMO/SYNTHETIC' : ''}`
              : 'Activate a model on the Models page'
          }
        />
      </section>

      <section className="mt-8 grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        <article className="rounded-xl border border-line bg-card p-6">
          <h2 className="font-serif text-2xl text-ink">Stored type counts</h2>
          <p className="mt-1 text-sm text-slate">
            {classified
              ? `${classified} classified assessment${classified === 1 ? '' : 's'}.`
              : 'No stored classifications yet.'}
          </p>
          <ul className="mt-6 space-y-3">
            {TYPES.map((item) => {
              const value = counts?.[item.key] ?? 0
              return (
                <li key={item.key}>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-slate">{item.name}</span>
                    <span className="font-medium text-ink">{value}</span>
                  </div>
                  <div className="mt-1 h-2 overflow-hidden rounded-full bg-sand">
                    <div
                      className="h-full rounded-full"
                      style={{
                        width: `${(value / maxCount) * 100}%`,
                        background: item.color,
                      }}
                    />
                  </div>
                </li>
              )
            })}
          </ul>
        </article>

        <aside className="space-y-4">
          <Link
            to="/admin/users"
            className="block rounded-xl border border-line bg-card px-5 py-4 hover:border-teal"
          >
            <p className="font-serif text-xl text-ink">Users</p>
            <p className="mt-1 text-sm text-slate">Accounts and roles</p>
          </Link>
          <Link
            to="/admin/assessments"
            className="block rounded-xl border border-line bg-card px-5 py-4 hover:border-teal"
          >
            <p className="font-serif text-xl text-ink">Assessments</p>
            <p className="mt-1 text-sm text-slate">Status and stored type, not answers</p>
          </Link>
          <Link
            to="/admin/models"
            className="block rounded-xl border border-line bg-card px-5 py-4 hover:border-teal"
          >
            <p className="font-serif text-xl text-ink">Models</p>
            <p className="mt-1 text-sm text-slate">Registry, activate and archive</p>
          </Link>
          <Link
            to="/admin/analytics"
            className="block rounded-xl border border-line bg-card px-5 py-4 hover:border-teal"
          >
            <p className="font-serif text-xl text-ink">Analytics</p>
            <p className="mt-1 text-sm text-slate">Stored counts and trends</p>
          </Link>
          <Link
            to="/admin/audit"
            className="block rounded-xl border border-line bg-card px-5 py-4 hover:border-teal"
          >
            <p className="font-serif text-xl text-ink">Audit log</p>
            <p className="mt-1 text-sm text-slate">Admin actions, not Likert answers</p>
          </Link>
        </aside>
      </section>
    </div>
  )
}
