import { useState, useEffect } from 'react'
import { authService } from '../services/authService'

export const useAuth = () => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false)
  const [isLoading, setIsLoading] = useState<boolean>(true)

  useEffect(() => {
    const checkAuthStatus = () => {
      const authStatus = authService.isAuthenticated()
      setIsAuthenticated(authStatus)
      setIsLoading(false)
    }

    checkAuthStatus()
  }, [])

  const login = async (username: string, password: string) => {
    try {
      const response = await authService.login({ username, password })
      if (response.access_token) {
        localStorage.setItem('token', response.access_token)
        setIsAuthenticated(true)
        return { success: true }
      } else {
        return { 
          success: false, 
          error: 'Login failed: Invalid response from server' 
        }
      }
    } catch (error: any) {
      // 处理不同类型的错误
      if (error.response) {
        // 服务器返回错误响应
        switch (error.response.status) {
          case 401:
            return { 
              success: false, 
              error: 'Invalid username or password' 
            }
          case 500:
            return { 
              success: false, 
              error: 'Server error. Please try again later.' 
            }
          default:
            return { 
              success: false, 
              error: error.response?.data?.detail || `Login failed with status ${error.response.status}` 
            }
        }
      } else if (error.request) {
        // 请求已发出但没有收到响应
        return { 
          success: false, 
          error: 'Network error. Please check your connection.' 
        }
      } else {
        // 其他错误
        return { 
          success: false, 
          error: error.message || 'Login failed' 
        }
      }
    }
  }

  const logout = () => {
    authService.logout()
    setIsAuthenticated(false)
  }

  return { isAuthenticated, isLoading, login, logout }
}