import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react'
import apiClient, { TOKEN_STORAGE_KEY } from '../api/client'

const AuthContext = createContext(null)

function saveSession(data, setUser) {
  if (!data || typeof data.token !== 'string' || !data.user) {
    throw new Error('The server returned an incomplete sign-in response.')
  }

  localStorage.setItem(TOKEN_STORAGE_KEY, data.token)
  setUser(data.user)
  return data.user
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let active = true
    const token = localStorage.getItem(TOKEN_STORAGE_KEY)

    if (!token) {
      setLoading(false)
      return () => {
        active = false
      }
    }

    apiClient
      .get('/api/auth/me')
      .then(({ data }) => {
        if (active) setUser(data.user)
      })
      .catch(() => {
        if (active) setUser(null)
      })
      .finally(() => {
        if (active) setLoading(false)
      })

    return () => {
      active = false
    }
  }, [])

  const login = useCallback(async (credentials) => {
    const { data } = await apiClient.post('/api/auth/login', {
      email: credentials.email,
      password: credentials.password,
    })
    return saveSession(data, setUser)
  }, [])

  const register = useCallback(async (details) => {
    const { data } = await apiClient.post('/api/auth/register', {
      name: details.name,
      email: details.email,
      password: details.password,
    })
    return saveSession(data, setUser)
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_STORAGE_KEY)
    setUser(null)
  }, [])

  const value = useMemo(
    () => ({ user, loading, login, register, logout }),
    [user, loading, login, register, logout],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)

  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider.')
  }

  return context
}
