import { useEffect, useState } from 'react'
import { fetchAdminUsers } from '../../api/admin'
import TableShell from '../../components/ui/TableShell'

export default function UsersPage() {
  const [rows, setRows] = useState([])
  const [error, setError] = useState(null)
  const [loaded, setLoaded] = useState(false)

  useEffect(() => {
    fetchAdminUsers()
      .then((response) => setRows(response.data.data ?? []))
      .catch((err) => {
        setError(err.response?.data?.message || 'Could not load users.')
      })
      .finally(() => setLoaded(true))
  }, [])

  return (
    <div>
      <p className="text-sm font-medium text-teal">Administration</p>
      <h1 className="mt-1 font-serif text-3xl text-ink">Users</h1>
      <p className="mt-2 max-w-2xl text-slate">
        This table is the protected user catalogue. Passwords are never
        returned.
      </p>

      {error && (
        <p className="mt-6 text-sm text-red-800" role="alert">
          {error}
        </p>
      )}

      {!loaded && !error && <p className="mt-8 text-slate">Loading accounts…</p>}

      {loaded && (
        <TableShell>
          <table className="min-w-full text-left text-sm">
            <thead className="border-b border-line text-xs uppercase tracking-wide text-muted">
              <tr>
                <th className="px-4 py-3">Name</th>
                <th className="px-4 py-3">Email</th>
                <th className="px-4 py-3">Role</th>
                <th className="px-4 py-3">Age group</th>
                <th className="px-4 py-3">Status</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.id} className="border-b border-line last:border-0">
                  <td className="px-4 py-3 text-ink">
                    {row.first_name} {row.last_name}
                  </td>
                  <td className="px-4 py-3 text-slate">{row.email}</td>
                  <td className="px-4 py-3 uppercase tracking-wide text-muted">
                    {row.role?.code}
                  </td>
                  <td className="px-4 py-3 text-slate">
                    {row.age_group ? row.age_group.replaceAll('_', ' ') : '—'}
                  </td>
                  <td className="px-4 py-3 text-slate">
                    {row.is_active ? 'Active' : 'Inactive'}
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
