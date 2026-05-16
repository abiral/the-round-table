import { useCallback, useEffect, useState } from 'react'
import { apiFetch, apiJson, ApiError } from '../lib/apiFetch'

export interface AuthUser {
  id: string
  firstname: string
  lastname: string
  email: string
}

interface AuthState {
  user: AuthUser | null
  loading: boolean
  error: string | null
}

export function useAuth() {
  const [state, setState] = useState<AuthState>({ user: null, loading: true, error: null })

  // Probe /me on mount to see if the cookie is still valid.
  useEffect(() => {
    let cancelled = false
    ;(async () => {
      try {
        const user = await apiJson<AuthUser>('/api/auth/me')
        if (!cancelled) setState({ user, loading: false, error: null })
      } catch (err) {
        if (cancelled) return
        if (err instanceof ApiError && err.status === 401) {
          setState({ user: null, loading: false, error: null })
        } else {
          setState({ user: null, loading: false, error: err instanceof Error ? err.message : 'Auth check failed' })
        }
      }
    })()
    return () => { cancelled = true }
  }, [])

  const login = useCallback(async (email: string, password: string) => {
    setState(prev => ({ ...prev, loading: true, error: null }))
    try {
      const user = await apiJson<AuthUser>('/api/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      })
      setState({ user, loading: false, error: null })
    } catch (err) {
      const msg = err instanceof ApiError ? err.message : (err instanceof Error ? err.message : 'Login failed')
      setState({ user: null, loading: false, error: msg })
      throw err
    }
  }, [])

  const logout = useCallback(async () => {
    try {
      await apiFetch('/api/auth/logout', { method: 'POST' })
    } finally {
      setState({ user: null, loading: false, error: null })
    }
  }, [])

  return { ...state, login, logout }
}
