import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { fetchHistory } from '../../api/history'
import TableShell from '../../components/ui/TableShell'
import { classifyAssessment } from '../../api/predictions'

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

function statusLabel(status) {
  return status.replaceAll('_', ' ').toLowerCase()
}

export default function AssessmentHistoryPage() {
  const navigate = useNavigate()
  const [rows, setRows] = useState([])
  const [error, setError] = useState(null)
  const [busyId, setBusyId] = useState(null)
  const [loaded, setLoaded] = useState(false)

  useEffect(() => {
    fetchHistory()
      .then((response) => setRows(response.data.data ?? []))
      .catch((err) => {
        setError(err.response?.data?.message || 'Could not load assessment history.')
      })
      .finally(() => setLoaded(true))
  }, [])

  async function handleClassify(assessmentId) {
    setBusyId(assessmentId)
    setError(null)
    try {
      await classifyAssessment(assessmentId)
      navigate(`/app/results?assessment_id=${assessmentId}`)
    } catch (err) {
      if (err.response?.status === 409) {
        navigate(`/app/results?assessment_id=${assessmentId}`)
        return
      }
      setError(
        err.response?.data?.message ||
          'Classification could not be completed. The answers are still stored.',
      )
    } finally {
      setBusyId(null)
    }
  }

  return (
    <div>
      <p className="text-sm font-medium text-teal">Your workspace</p>
      <h1 className="mt-1 font-serif text-2xl text-ink sm:text-3xl">Assessment history</h1>
      <p className="mt-2 max-w-2xl text-slate">
        These rows are your saved attempts. A type and confidence appear only
        after classification. Mix percentages stay on the results page.
      </p>

      {error && (
        <p className="mt-6 text-sm text-red-800" role="alert">
          {error}
        </p>
      )}

      {!loaded && !error && (
        <p className="mt-8 text-slate">Loading your saved assessments…</p>
      )}

      {loaded && rows.length === 0 && !error && (
        <div className="mt-8 rounded-xl border border-dashed border-line bg-card px-6 py-10 text-center">
          <p className="font-serif text-xl text-ink">No assessments yet</p>
          <p className="mt-2 text-sm text-slate">
            History stays empty until you start a questionnaire.
          </p>
          <Link
            to="/app/assessment"
            className="mt-6 inline-flex rounded-md bg-teal px-4 py-2.5 text-sm font-medium text-white hover:bg-teal-dark"
          >
            Take assessment
          </Link>
        </div>
      )}

      {rows.length > 0 && (
        <TableShell>
          <table className="min-w-full text-left text-sm">
            <thead className="border-b border-line text-xs uppercase tracking-wide text-muted">
              <tr>
                <th className="px-4 py-3">Date</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Indicated type</th>
                <th className="px-4 py-3">Confidence</th>
                <th className="px-4 py-3">Progress</th>
                <th className="px-4 py-3"> </th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.assessment_id} className="border-b border-line last:border-0">
                  <td className="px-4 py-3 text-ink">
                    {formatDate(row.completed_at || row.started_at)}
                    <span className="mt-1 block text-xs text-muted">
                      #{row.assessment_id}
                    </span>
                  </td>
                  <td className="px-4 py-3 capitalize text-slate">{statusLabel(row.status)}</td>
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
                  <td className="px-4 py-3 text-right">
                    {row.status === 'IN_PROGRESS' && (
                      <Link to="/app/assessment" className="text-sm font-medium text-teal">
                        Continue
                      </Link>
                    )}
                    {row.status === 'COMPLETED' && row.has_prediction && (
                      <Link
                        to={`/app/results?assessment_id=${row.assessment_id}`}
                        className="text-sm font-medium text-teal"
                      >
                        View result
                      </Link>
                    )}
                    {row.status === 'COMPLETED' && !row.has_prediction && (
                      <button
                        type="button"
                        disabled={busyId === row.assessment_id}
                        onClick={() => handleClassify(row.assessment_id)}
                        className="text-sm font-medium text-teal disabled:opacity-50"
                      >
                        {busyId === row.assessment_id ? 'Classifying…' : 'Classify'}
                      </button>
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
