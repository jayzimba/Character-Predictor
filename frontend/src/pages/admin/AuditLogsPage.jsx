import { useEffect, useMemo, useState } from 'react'
import { fetchAuditLogs } from '../../api/admin'
import IconButton, { ChevronIcon } from '../../components/ui/IconButton'
import TableShell from '../../components/ui/TableShell'

const PAGE_SIZE = 10

function formatWhen(value) {
  if (!value) {
    return '—'
  }
  return new Intl.DateTimeFormat('en-GB', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value))
}

function formatDetails(details) {
  if (!details || typeof details !== 'object') {
    return '—'
  }
  const parts = Object.entries(details)
    .filter(([, item]) => item !== null && item !== undefined && item !== '')
    .map(([key, item]) => `${key}: ${Array.isArray(item) ? item.join(', ') : item}`)
  return parts.length ? parts.join(' · ') : '—'
}

export default function AuditLogsPage() {
  const [payload, setPayload] = useState({ items: [], total: 0, disclaimer: '' })
  const [error, setError] = useState(null)
  const [loaded, setLoaded] = useState(false)
  const [page, setPage] = useState(1)

  useEffect(() => {
    fetchAuditLogs()
      .then((response) => setPayload(response.data.data ?? { items: [], total: 0 }))
      .catch((err) => {
        setError(err.response?.data?.message || 'Could not load the audit log.')
      })
      .finally(() => setLoaded(true))
  }, [])

  const rows = payload.items ?? []
  const pageCount = Math.max(1, Math.ceil(rows.length / PAGE_SIZE))
  const currentPage = Math.min(page, pageCount)
  const visible = useMemo(() => {
    const start = (currentPage - 1) * PAGE_SIZE
    return rows.slice(start, start + PAGE_SIZE)
  }, [rows, currentPage])
  const rangeStart = rows.length === 0 ? 0 : (currentPage - 1) * PAGE_SIZE + 1
  const rangeEnd = Math.min(currentPage * PAGE_SIZE, rows.length)

  return (
    <div>
      <p className="text-sm font-medium text-teal">Administration</p>
      <h1 className="mt-1 font-serif text-3xl text-ink">Audit log</h1>
      <p className="mt-2 max-w-2xl text-slate">
        Administrator actions already stored in MySQL. Likert answers and
        passwords are not written here.
      </p>

      {loaded && payload.disclaimer && (
        <p className="mt-6 rounded-xl border border-line bg-card px-4 py-3 text-sm text-slate">
          {payload.disclaimer}
        </p>
      )}

      {error && (
        <p className="mt-6 text-sm text-red-800" role="alert">
          {error}
        </p>
      )}

      {!loaded && !error && <p className="mt-8 text-slate">Loading audit log…</p>}

      {loaded && (
        <>
          <TableShell>
            <table className="min-w-full text-left text-sm">
              <thead className="border-b border-line text-xs uppercase tracking-wide text-muted">
                <tr>
                  <th className="px-4 py-3">When</th>
                  <th className="px-4 py-3">Actor</th>
                  <th className="px-4 py-3">Action</th>
                  <th className="px-4 py-3">Entity</th>
                  <th className="px-4 py-3">Details</th>
                </tr>
              </thead>
              <tbody>
                {visible.length === 0 && (
                  <tr>
                    <td className="px-4 py-6 text-slate" colSpan={5}>
                      No audited actions yet. Activating a model or changing a
                      question writes a row.
                    </td>
                  </tr>
                )}
                {visible.map((row) => (
                  <tr key={row.id} className="border-b border-line last:border-0">
                    <td className="whitespace-nowrap px-4 py-3 text-slate">
                      {formatWhen(row.created_at)}
                    </td>
                    <td className="px-4 py-3 text-ink">{row.actor_email || 'System'}</td>
                    <td className="px-4 py-3 font-medium text-ink">{row.action}</td>
                    <td className="px-4 py-3 text-slate">
                      {row.entity_type || '—'}
                      {row.entity_id ? ` #${row.entity_id}` : ''}
                    </td>
                    <td className="px-4 py-3 text-slate">{formatDetails(row.details)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </TableShell>
          <div className="mt-4 flex flex-wrap items-center justify-between gap-3 text-sm text-slate">
            <p>
              {rows.length
                ? `${rangeStart}–${rangeEnd} of ${rows.length}`
                : '0 rows'}
            </p>
            <div className="flex items-center gap-1">
              <IconButton
                label="Previous page"
                disabled={currentPage <= 1}
                onClick={() => setPage((value) => Math.max(1, value - 1))}
              >
                <ChevronIcon direction="prev" />
              </IconButton>
              <IconButton
                label="Next page"
                disabled={currentPage >= pageCount}
                onClick={() => setPage((value) => Math.min(pageCount, value + 1))}
              >
                <ChevronIcon direction="next" />
              </IconButton>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
