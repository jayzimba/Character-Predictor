import { useEffect, useState } from 'react'
import { fetchAdminQuestions } from '../../api/questions'

export default function QuestionsPage() {
  const [rows, setRows] = useState([])
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchAdminQuestions()
      .then((response) => setRows(response.data.data ?? []))
      .catch((err) => {
        setError(err.response?.data?.message || 'Could not load questions.')
      })
  }, [])

  return (
    <div>
      <p className="text-sm font-medium text-teal">Instrument catalogue</p>
      <h1 className="mt-1 font-serif text-3xl text-ink">Questions</h1>
      <p className="mt-2 max-w-2xl text-slate">
        These rows come from MySQL. Create, edit and deactivate stay for the
        later admin-questions phase so historical answers stay reproducible.
      </p>

      {error && (
        <p className="mt-6 text-sm text-red-800" role="alert">
          {error}
        </p>
      )}

      <div className="mt-8 overflow-x-auto rounded-xl border border-line bg-card">
        <table className="min-w-full text-left text-sm">
          <thead className="border-b border-line text-xs uppercase tracking-wide text-muted">
            <tr>
              <th className="px-4 py-3">#</th>
              <th className="px-4 py-3">Question</th>
              <th className="px-4 py-3">Category</th>
              <th className="px-4 py-3">Trait</th>
              <th className="px-4 py-3">Weight</th>
              <th className="px-4 py-3">Reverse</th>
              <th className="px-4 py-3">Status</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.id} className="border-b border-line last:border-b-0">
                <td className="px-4 py-3 text-muted">{row.display_order}</td>
                <td className="max-w-md px-4 py-3 text-ink">{row.question_text}</td>
                <td className="px-4 py-3 text-slate">{row.category.name}</td>
                <td className="px-4 py-3 text-slate">{row.personality_trait?.name ?? '—'}</td>
                <td className="px-4 py-3 text-slate">{row.weight}</td>
                <td className="px-4 py-3 text-slate">{row.reverse_scored ? 'Yes' : 'No'}</td>
                <td className="px-4 py-3 text-slate">{row.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
