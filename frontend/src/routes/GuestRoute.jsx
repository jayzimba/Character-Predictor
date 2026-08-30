import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function GuestRoute() {
  const { user, loading, isAdmin } = useAuth()

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-paper text-muted">
        Checking your session…
      </div>
    )
  }

  if (user) {
    return <Navigate to={isAdmin ? '/admin' : '/app'} replace />
  }

  return <Outlet />
}
