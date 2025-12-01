import { Navigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

interface ProtectedAdminRouteProps {
  children: React.ReactNode
}

const ProtectedAdminRoute = ({ children }: ProtectedAdminRouteProps) => {
  const { isAuthenticated, user, loading } = useAuth()

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  if (user?.is_admin !== 1) {
    return (
      <div className="text-center py-12">
        <h1 className="text-2xl font-bold text-red-600 mb-4">Доступ запрещен</h1>
        <p className="text-gray-600">У вас нет прав для доступа к этой странице</p>
      </div>
    )
  }

  return <>{children}</>
}

export default ProtectedAdminRoute

