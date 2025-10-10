import React from 'react'
import { Routes, Route, Navigate, useLocation } from 'react-router-dom'
import Login from './pages/Login'
import Chat from './pages/Chat'
import { useAuth } from './hooks/useAuth'

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth()
  const location = useLocation()

  if (isLoading) {
    return <div>Loading...</div>
  }

  if (!isAuthenticated) {
    // 保存用户尝试访问的路径，以便登录后重定向
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  return <>{children}</>
}

const App: React.FC = () => {
  const { isAuthenticated, isLoading } = useAuth()
  const location = useLocation()

  if (isLoading) {
    return <div>Loading...</div>
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Routes>
        <Route 
          path="/login" 
          element={isAuthenticated ? <Navigate to="/chat" replace /> : <Login />} 
        />
        <Route 
          path="/chat" 
          element={
            <ProtectedRoute>
              <Chat />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/" 
          element={
            isAuthenticated 
              ? <Navigate to="/chat" replace /> 
              : <Navigate to="/login" state={{ from: location }} replace />
          } 
        />
      </Routes>
    </div>
  )
}

export default App