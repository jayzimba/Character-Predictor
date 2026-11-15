import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { fetchAdminAssessments } from '../../api/admin'
import TableShell from '../../components/ui/TableShell'

function formatDate(value) {
  if (!value) {
    return '—'
  }
  return new Intl.DateTimeFormat('en-GB', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  }).format(new Date(value))
}

function formatConfidence(score) {
  if (score == null) {
    return '—'
  }
  return `${Math.round(score * 100)}%`
}

export default function AssessmentsPage() {
  const [rows, setRows] = useState([])
  const [error, setError] = useState(null)
  const [loaded, setLoaded] = useState(false)

  useEffect(() => {
    fetchAdminAssessments()
      .then((response) => setRows(response.data.data ?? []))
      .catch((err) => {
        setError(err.response?.data?.message || 'Could not load assessments.')
      })
      .finally(() => setLoaded(true))
  }, [])

  return (
    <div>
      <p className="text-sm font-medium text-teal">Administration</p>
      <h1 className="mt-1 font-serif text-3xl text-ink">Assessments</h1>
      <p className="mt-2 max-w-2xl text-slate">
        Overview of submissions. Likert answers are not shown here.
      </p>

      {error && (
        <p className="mt-6 text-sm text-red-800" role="alert">
          {error}
        </p>
      )}

      {!loaded && !error && (
        <p className="mt-8 text-slate">Loading assessments…</p>
      )}

      {loaded && rows.length === 0 && !error && (
        <p className="mt-8 text-slate">No assessments have been started yet.</p>
      )}

      {loaded && rows.length > 0 && (
        <TableShell>
          <table className="min-w-full text-left text-sm">
            <thead className="border-b border-line text-xs uppercase tracking-wide text-muted">
              <tr>
                <th className="px-4 py-3">Participant</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Indicated type</th>
                <th className="px-4 py-3">Confidence</th>
                <th className="px-4 py-3">Progress</th>
                <th className="px-4 py-3">Date</th>
                <th className="px-4 py-3"> </th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.assessment_id} className="border-b border-line last:border-0">
                  <td className="px-4 py-3">
                    <span className="text-ink">{row.user_name}</span>
                    <span className="mt-1 block text-xs text-muted">{row.user_email}</span>
                  </td>
                  <td className="px-4 py-3 capitalize text-slate">
                    {row.status.replaceAll('_', ' ').toLowerCase()}
                  </td>
                  <td className="px-4 py-3">
                    {row.has_prediction ? (
                      <span className="text-ink">
                        {row.personality_name}
                        {row.is_demo_mode && (
                          <span className="ml-2 rounded-full bg-sand px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-slate">
                            Demo
                          </span>
                        )}
                      </span>
                    ) : (
                      <span className="text-muted">None yet</span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-ink">{formatConfidence(row.confidence)}</td>
                  <td className="px-4 py-3 text-slate">
                    {row.answered} of {row.total}
                  </td>
                  <td className="px-4 py-3 text-slate">
                    {formatDate(row.completed_at || row.started_at)}
                    <span className="mt-1 block text-xs text-muted">#{row.assessment_id}</span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    {row.has_prediction && (
                      <Link
                        to={`/app/results?assessment_id=${row.assessment_id}`}
                        className="text-sm font-medium text-teal"
                      >
                        View result
                      </Link>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </TableShell>
      )}
    </div>
  )
}
