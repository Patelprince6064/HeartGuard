import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'

const AuthContext = createContext(null)

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used within an AuthProvider')
  return context
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(localStorage.getItem('heartguard_token'))
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  const loadUser = useCallback(async () => {
    const storedToken = localStorage.getItem('heartguard_token')
    if (storedToken) {
      try {
        const res = await api.auth.getMe()
        setUser(res.data)
      } catch {
        localStorage.removeItem('heartguard_token')
        setToken(null)
        setUser(null)
      }
    }
    setLoading(false)
  }, [])

  useEffect(() => {
    loadUser()
  }, [loadUser])

  const login = async (email, password) => {
    const res = await api.auth.login(email, password)
    const { access_token, user: userData } = res.data
    localStorage.setItem('heartguard_token', access_token)
    setToken(access_token)
    setUser(userData)
    return userData
  }

  const register = async (data) => {
    const res = await api.auth.register(data)
    const { access_token, user: userData } = res.data
    localStorage.setItem('heartguard_token', access_token)
    setToken(access_token)
    setUser(userData)
    return userData
  }

  const logout = () => {
    localStorage.removeItem('heartguard_token')
    setToken(null)
    setUser(null)
    navigate('/login')
  }

  const isAuthenticated = !!token && !!user

  const hasRole = (roles) => {
    if (!user) return false
    if (typeof roles === 'string') return user.role === roles
    return roles.includes(user.role)
  }

  return (
    <AuthContext.Provider value={{ user, token, loading, login, logout, register, isAuthenticated, hasRole }}>
      {children}
    </AuthContext.Provider>
  )
}
