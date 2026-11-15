import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { fetchAnalytics } from '../../api/analytics'
import StatCard from '../../components/dashboard/StatCard'

const TYPES = [
  { key: 'choleric', name: 'Choleric', color: '#c45c26' },
  { key: 'melancholic', name: 'Melancholic', color: '#3d4f66' },
  { key: 'phlegmatic', name: 'Phlegmatic', color: '#0f6e68' },
  { key: 'sanguine', name: 'Sanguine', color: '#b0893e' },
]

function Notice({ tone = 'slate', children }) {
  const tones = {
    slate: 'border-line bg-card text-slate',
    amber: 'border-amber-200 bg-amber-50 text-amber-950',
    teal: 'border-teal/30 bg-teal/5 text-teal-dark',
    danger: 'border-red-200 bg-red-50 text-red-800',
  }
  return (
    <p className={`rounded-xl border px-4 py-3 text-sm ${tones[tone]}`} role={tone === 'danger' ? 'alert' : undefined}>
      {children}
    </p>
  )
}

function TabButton({ id, label, current, onSelect }) {
  const selected = current === id
  return (
    <button
      type="button"
      role="tab"
      id={`analytics-tab-${id}`}
      aria-selected={selected}
      aria-controls={`analytics-panel-${id}`}
      onClick={() => onSelect(id)}
      className={`rounded-md px-4 py-2 text-sm font-medium ${
        selected ? 'bg-teal text-white' : 'text-slate hover:bg-sand hover:text-ink'
      }`}
    >
      {label}
    </button>
  )
}

function formatPercent(value) {
  if (typeof value !== 'number' || Number.isNaN(value)) {
    return '—'
  }
  return `${Math.round(value * 100)}%`
}

function formatDay(value) {
  return new Intl.DateTimeFormat('en-GB', { day: 'numeric', month: 'short' }).format(new Date(`${value}T00:00:00`))
}

function ChartCard({ title, hint, children, empty }) {
  return (
    <article className="rounded-xl border border-line bg-card p-5">
      <h2 className="font-serif text-2xl text-ink">{title}</h2>
      {hint && <p className="mt-1 text-sm text-slate">{hint}</p>}
      <div className="mt-4">{empty ? <p className="py-10 text-sm text-slate">{empty}</p> : children}</div>
    </article>
  )
}

function CountBars({ rows, color = '#0f6e68' }) {
  if (!rows?.length) {
    return null
  }
  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={rows} margin={{ top: 8, right: 16, left: 8, bottom: 8 }}>
          <CartesianGrid stroke="#d9d2c8" vertical={false} />
          <XAxis dataKey="label" tick={{ fill: '#3d4f66', fontSize: 12 }} />
          <YAxis allowDecimals={false} width={36} tick={{ fill: '#6b7a8d', fontSize: 12 }} />
          <Tooltip />
          <Bar dataKey="count" fill={color} radius={[4, 4, 0, 0]} maxBarSize={72} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

function buildNotices(data) {
  if (!data) {
    return []
  }
  const items = []
  const { totals } = data
  if (totals.classifications_stored === 0) {
    items.push({
      tone: 'slate',
      text: 'No stored classifications yet. Totals stay at zero until a completed assessment is classified.',
    })
    return items
  }
  if (totals.demo_classifications === totals.classifications_stored) {
    items.push({
      tone: 'amber',
      text: `All ${totals.classifications_stored} stored classification${totals.classifications_stored === 1 ? '' : 's'} are DEMO MODE. Do not put this distribution in the report as research findings.`,
    })
  } else if (totals.demo_classifications > 0) {
    items.push({
      tone: 'amber',
      text: `${totals.demo_classifications} of ${totals.classifications_stored} stored classifications are DEMO MODE. Filter them out before discussing research results.`,
    })
  } else {
    items.push({
      tone: 'teal',
      text: `${totals.classifications_stored} stored classification${totals.classifications_stored === 1 ? '' : 's'} are counted from live predictions, not DEMO MODE.`,
    })
  }
  return items
}

export default function AnalyticsPage() {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const [loaded, setLoaded] = useState(false)
  const [tab, setTab] = useState('distribution')

  useEffect(() => {
    fetchAnalytics()
      .then((response) => setData(response.data.data))
      .catch((err) => {
        setError(err.response?.data?.message || 'Could not load analytics.')
      })
      .finally(() => setLoaded(true))
  }, [])

  const notices = useMemo(() => buildNotices(data), [data])
  const totals = data?.totals
  const personalityRows = TYPES.map((item) => ({
    key: item.key,
    label: item.name,
    count: data?.personality_counts?.[item.key] ?? 0,
    fill: item.color,
  }))
  const classified = totals?.classifications_stored ?? 0
  const maxPersonality = Math.max(...personalityRows.map((row) => row.count), 1)
  const trendRows = (data?.series ?? []).map((point) => ({
    ...point,
    label: formatDay(point.date),
  }))
  const activeDays = trendRows.filter(
    (point) => point.started || point.completed || point.classified || point.demo,
  )
  const hasTrend = activeDays.length > 0

  return (
    <div>
      <p className="text-sm font-medium text-teal">Administration</p>
      <h1 className="mt-1 font-serif text-2xl text-ink sm:text-3xl">Analytics</h1>
      <p className="mt-2 max-w-2xl text-slate">
        Aggregates of assessments and stored predictions. Likert answers are
        not shown. Charts count what is already in MySQL — they do not run a
        new classifier.
      </p>

      <div className="mt-6 space-y-3">
        {loaded &&
          notices.map((item) => (
            <Notice key={item.text} tone={item.tone}>
              {item.text}
            </Notice>
          ))}
        {error && <Notice tone="danger">{error}</Notice>}
      </div>

      <section className="mt-8 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label="Classifications stored"
          value={totals ? totals.classifications_stored : '—'}
          hint={
            totals
              ? `${totals.demo_classifications} DEMO MODE · ${totals.model_classifications} not DEMO`
              : 'From prediction_results'
          }
        />
        <StatCard
          label="Assessments completed"
          value={totals ? totals.assessments_completed : '—'}
          hint={
            totals?.assessments_in_progress
              ? `${totals.assessments_in_progress} still in progress`
              : 'Finished submissions'
          }
        />
        <StatCard
          label="Completion rate"
          value={totals ? formatPercent(totals.completion_rate) : '—'}
          hint="Completed ÷ started, from stored rows"
        />
        <StatCard
          label="Mean confidence"
          value={totals?.mean_confidence != null ? formatPercent(totals.mean_confidence) : '—'}
          hint="Average of stored confidence_score"
        />
      </section>

      <div
        role="tablist"
        aria-label="Analytics"
        className="mt-8 inline-flex flex-wrap gap-1 rounded-lg border border-line bg-card p-1"
      >
        <TabButton id="distribution" label="Distribution" current={tab} onSelect={setTab} />
        <TabButton id="trends" label="Trends" current={tab} onSelect={setTab} />
        <TabButton id="participants" label="Participants" current={tab} onSelect={setTab} />
      </div>

      {tab === 'distribution' && (
        <section
          id="analytics-panel-distribution"
          role="tabpanel"
          aria-labelledby="analytics-tab-distribution"
          className="mt-6 grid gap-6 xl:grid-cols-2"
        >
          <ChartCard
            title="Stored type counts"
            hint="Count of predicted_personality on stored results, not a fresh prediction."
          >
            <ul className="space-y-3">
              {personalityRows.map((item) => (
                <li key={item.key}>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-slate">{item.label}</span>
                    <span className="font-medium text-ink">{item.count}</span>
                  </div>
                  <div className="mt-1 h-2 overflow-hidden rounded-full bg-sand">
                    <div
                      className="h-full rounded-full"
                      style={{
                        width: classified ? `${(item.count / maxPersonality) * 100}%` : '0%',
                        background: item.fill,
                      }}
                    />
                  </div>
                </li>
              ))}
            </ul>
          </ChartCard>

          <ChartCard
            title="Prediction source"
            hint="DEMO MODE is labelled on the stored row. It is not inferred here."
            empty={classified === 0 ? 'No stored classifications to split by source.' : null}
          >
            <CountBars rows={data?.source_counts} color="#b0893e" />
          </ChartCard>

          <ChartCard
            title="Linked algorithm"
            hint="From ml_models.algorithm on the stored prediction. NONE means no model_id."
            empty={!data?.algorithm_counts?.length ? 'No model links on stored predictions yet.' : null}
          >
            <CountBars rows={data?.algorithm_counts} />
          </ChartCard>
        </section>
      )}

      {tab === 'trends' && (
        <section
          id="analytics-panel-trends"
          role="tabpanel"
          aria-labelledby="analytics-tab-trends"
          className="mt-6"
        >
          <ChartCard
            title="Activity over time"
            hint="Each point is a calendar day that has stored activity, plus the last 14 days. Days with no rows are zero, not estimated."
            empty={!hasTrend ? 'No assessment activity in this window.' : null}
          >
            {activeDays.length > 0 && (
              <ul className="mb-4 grid gap-2 text-sm text-slate sm:grid-cols-2 xl:grid-cols-3">
                {activeDays.map((point) => (
                  <li key={point.date} className="rounded-lg border border-line bg-sand/40 px-3 py-2">
                    <span className="font-medium text-ink">{point.label}</span>
                    {': '}
                    {point.started} started · {point.completed} completed · {point.classified} classified
                    {point.demo ? ` · ${point.demo} DEMO` : ''}
                  </li>
                ))}
              </ul>
            )}
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={trendRows} margin={{ top: 8, right: 12, left: 8, bottom: 28 }}>
                  <CartesianGrid stroke="#d9d2c8" vertical={false} />
                  <XAxis
                    dataKey="label"
                    interval={0}
                    angle={-35}
                    textAnchor="end"
                    height={48}
                    tick={{ fill: '#3d4f66', fontSize: 11 }}
                  />
                  <YAxis allowDecimals={false} width={36} tick={{ fill: '#6b7a8d', fontSize: 12 }} />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="started" name="Started" fill="#3d4f66" radius={[4, 4, 0, 0]} maxBarSize={22} />
                  <Bar dataKey="completed" name="Completed" fill="#0f6e68" radius={[4, 4, 0, 0]} maxBarSize={22} />
                  <Bar dataKey="classified" name="Classified" fill="#c45c26" radius={[4, 4, 0, 0]} maxBarSize={22} />
                  <Bar dataKey="demo" name="DEMO MODE" fill="#b0893e" radius={[4, 4, 0, 0]} maxBarSize={22} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </ChartCard>
        </section>
      )}

      {tab === 'participants' && (
        <section
          id="analytics-panel-participants"
          role="tabpanel"
          aria-labelledby="analytics-tab-participants"
          className="mt-6 grid gap-6 xl:grid-cols-2"
        >
          <ChartCard
            title="Age group"
            hint="Unique participants who already have a stored classification. Optional field."
            empty={!data?.age_group_counts?.length ? 'No classified participants with age group data.' : null}
          >
            <CountBars rows={data?.age_group_counts} color="#3d4f66" />
          </ChartCard>
          <ChartCard
            title="Gender"
            hint="Unique classified participants. Values they chose on their profile, including not provided."
            empty={!data?.gender_counts?.length ? 'No classified participants with gender data.' : null}
          >
            <CountBars rows={data?.gender_counts} color="#0f6e68" />
          </ChartCard>
          <p className="text-sm text-slate xl:col-span-2">
            Participant counts never include Likert answers. Open{' '}
            <Link to="/admin/assessments" className="text-teal hover:text-teal-dark">
              Assessments
            </Link>{' '}
            for status and stored type only.
          </p>
        </section>
      )}
    </div>
  )
}
