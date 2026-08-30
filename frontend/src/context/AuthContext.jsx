import { createContext, useContext, useEffect, useMemo, useState } from 'react'
import { fetchCurrentUser, login as loginRequest, registerAccount } from '../api/auth'
import apiClient from '../api/client'
import { getAccessToken, setAccessToken } from '../utils/storage'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false

    async function restore() {
      if (!getAccessToken()) {
        setLoading(false)
        return
      }
      try {
        const response = await fetchCurrentUser()
        if (!cancelled) {
          setUser(response.data.data)
        }
      } catch {
        setAccessToken(null)
        if (!cancelled) {
          setUser(null)
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    restore()
    return () => {
      cancelled = true
    }
  }, [])

  useEffect(() => {
    const interceptor = apiClient.interceptors.response.use(
      (response) => response,
      (error) => {
        const url = error.config?.url || ''
        const isAuthAttempt =
          url.includes('/auth/login') || url.includes('/auth/register')
        if (error.response?.status === 401 && !isAuthAttempt) {
          setAccessToken(null)
          setUser(null)
        }
        return Promise.reject(error)
      },
    )
    return () => apiClient.interceptors.response.eject(interceptor)
  }, [])

  const value = useMemo(() => {
    async function applySession(payload) {
      setAccessToken(payload.access_token)
      setUser(payload.user)
      return payload.user
    }

    return {
      user,
      loading,
      isAuthenticated: Boolean(user),
      isAdmin: user?.role?.code === 'ADMIN',
      async login(email, password) {
        const response = await loginRequest(email, password)
        return applySession(response.data.data)
      },
      async register(payload) {
        const response = await registerAccount(payload)
        return applySession(response.data.data)
      },
      applyUser(nextUser) {
        setUser(nextUser)
        return nextUser
      },
      logout() {
        setAccessToken(null)
        setUser(null)
      },
    }
  }, [user, loading])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used inside AuthProvider')
  }
  return context
}
