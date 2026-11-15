import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { fetchDashboard } from '../../api/dashboard'
import PersonalityMixChart from '../../components/dashboard/PersonalityMixChart'
import StatCard from '../../components/dashboard/StatCard'
import { useAuth } from '../../context/AuthContext'

function formatDate(value) {
  if (!value) {
    return 'No assessment yet'
  }
  return new Intl.DateTimeFormat('en-GB', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  }).format(new Date(value))
}

function formatConfidence(score) {
  if (score == null) {
    return null
  }
  return `${Math.round(score * 100)}%`
}

export default function DashboardPage() {
  const { user } = useAuth()
  const [summary, setSummary] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchDashboard()
      .then((response) => setSummary(response.data.data))
      .catch((err) => {
        setError(err.response?.data?.message || 'Could not load the dashboard.')
      })
  }, [])

  const hasResult = Boolean(summary?.latest_personality)
  const completionHint = summary?.completion
    ? `${summary.completion.answered} of ${summary.completion.total} items · ${summary.completion.status.replaceAll('_', ' ').toLowerCase()}`
    : 'Start an assessment to begin'

  return (
    <div>
      <p className="text-sm font-medium text-teal">Your workspace</p>
      <h1 className="mt-1 font-serif text-2xl text-ink sm:text-3xl">Welcome back, {user.first_name}</h1>
      <p className="mt-2 max-w-2xl text-slate">
        This summary is read from your saved assessments. Cards stay empty until
        you complete a questionnaire — nothing here is invented.
      </p>

      {error && (
        <p className="mt-6 text-sm text-red-800" role="alert">
          {error}
        </p>
      )}

      <section className="mt-8 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
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
          label="Latest personality type"
          value={summary?.latest_personality?.name ?? 'None yet'}
          hint={
            summary?.latest_personality
              ? summary.latest_personality.tagline
              : 'Available after classification'
          }
        />
        <StatCard
          label="Latest assessment date"
          value={summary?.latest_assessment_at ? formatDate(summary.latest_assessment_at) : '—'}
          hint={
            formatConfidence(summary?.latest_confidence)
              ? `Confidence ${formatConfidence(summary.latest_confidence)}`
              : 'Date of your most recent completed test'
          }
        />
        <StatCard
          label="Assessment completion"
          value={summary?.completion ? `${summary.completion.percent}%` : '0%'}
          hint={completionHint}
        />
      </section>

      <section className="mt-8 grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        <article className="rounded-xl border border-line bg-card p-6">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <h2 className="font-serif text-2xl text-ink">Personality mix</h2>
              <p className="mt-1 text-sm text-slate">
                {hasResult
                  ? `Your latest assessment indicates ${summary.latest_personality.name}.`
                  : 'The mix is stored with the prediction, not estimated here.'}
              </p>
            </div>
            {summary?.is_demo_mode && (
              <span className="rounded-full bg-sand px-3 py-1 text-xs font-semibold uppercase tracking-wide text-slate">
                Demo mode
              </span>
            )}
          </div>
          <div className="mt-6">
            <PersonalityMixChart mix={summary?.latest_mix} />
          </div>
        </article>

        <aside className="space-y-4">
          <Link
            to="/app/assessment"
            className="block rounded-xl bg-teal px-5 py-4 text-white hover:bg-teal-dark"
          >
            <p className="text-xs font-semibold uppercase tracking-[0.14em] text-white/80">
              Next step
            </p>
            <p className="mt-2 font-serif text-xl">Take New Assessment</p>
            <p className="mt-1 text-sm text-white/80">
              {summary?.assessments_in_progress
                ? 'Continue your saved questionnaire'
                : 'Consent, answer, save and submit'}
            </p>
          </Link>
          <Link
            to="/app/results"
            className="block rounded-xl border border-line bg-card px-5 py-4 hover:border-teal"
          >
            <p className="font-serif text-xl text-ink">View My Results</p>
            <p className="mt-1 text-sm text-slate">
              {hasResult
                ? `${summary.latest_personality.name} · strengths, mix and development notes`
                : 'No stored result to open yet'}
            </p>
          </Link>
          <Link
            to="/app/history"
            className="block rounded-xl border border-line bg-card px-5 py-4 hover:border-teal"
          >
            <p className="font-serif text-xl text-ink">Assessment History</p>
            <p className="mt-1 text-sm text-slate">
              {summary
                ? `${summary.assessments_completed} completed`
                : 'Previous submissions'}
            </p>
          </Link>
          <Link
            to="/app/profile"
            className="block rounded-xl border border-line bg-card px-5 py-4 hover:border-teal"
          >
            <p className="font-serif text-xl text-ink">Profile</p>
            <p className="mt-1 text-sm text-slate">{user.email}</p>
          </Link>
        </aside>
      </section>
    </div>
  )
}
