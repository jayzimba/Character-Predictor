import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

function LoadingScreen() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-paper text-muted">
      Checking your session…
    </div>
  )
}

export default function ProtectedRoute({ roles }) {
  const { user, loading } = useAuth()
  const location = useLocation()

  if (loading) {
    return <LoadingScreen />
  }

  if (!user) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />
  }

  if (roles?.length && !roles.includes(user.role.code)) {
    return <Navigate to="/app" replace />
  }

  return <Outlet />
}
