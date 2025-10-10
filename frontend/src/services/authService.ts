import api from './api'

interface LoginCredentials {
  username: string
  password: string
}

interface LoginResponse {
  access_token: string
  token_type: string
}

export const authService = {
  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    const formData = new FormData()
    formData.append('username', credentials.username)
    formData.append('password', credentials.password)
    
    const response = await api.post<LoginResponse>('/login/token', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    
    return response.data
  },

  logout(): void {
    localStorage.removeItem('token')
  },

  isAuthenticated(): boolean {
    const token = localStorage.getItem('token')
    return !!token
  },
}