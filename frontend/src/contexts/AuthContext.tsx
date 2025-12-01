import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { authAPI } from '../api/client'

interface User {
  id: number
  name: string
  email: string
  phone?: string
  address?: string
  is_admin?: number
}

interface AuthContextType {
  user: User | null
  token: string | null
  login: (email: string, password: string) => Promise<void>
  register: (data: { name: string; email: string; password: string; phone?: string; address?: string }) => Promise<void>
  logout: () => void
  isAuthenticated: boolean
  loading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const storedToken = localStorage.getItem('token')
    const storedUser = localStorage.getItem('user')
    
    if (storedToken && storedUser) {
      setToken(storedToken)
      setUser(JSON.parse(storedUser))
      // Verify token is still valid
      authAPI.getMe()
        .then((response) => {
          setUser(response.data)
          localStorage.setItem('user', JSON.stringify(response.data))
        })
        .catch(() => {
          // Token invalid, clear storage
          localStorage.removeItem('token')
          localStorage.removeItem('user')
          setToken(null)
          setUser(null)
        })
        .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [])

  const login = async (email: string, password: string) => {
    const response = await authAPI.login(email, password)
    const { access_token } = response.data
    setToken(access_token)
    localStorage.setItem('token', access_token)
    
    // Get user info
    const userResponse = await authAPI.getMe()
    setUser(userResponse.data)
    localStorage.setItem('user', JSON.stringify(userResponse.data))
  }

  const register = async (data: { name: string; email: string; password: string; phone?: string; address?: string }) => {
    await authAPI.register(data)
    // Auto-login after registration
    await login(data.email, data.password)
  }

  const logout = () => {
    setToken(null)
    setUser(null)
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        login,
        register,
        logout,
        isAuthenticated: !!token,
        loading,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

