import { useCallback, useEffect, useState } from 'react'
import { apiFetch, apiJson, ApiError } from '../lib/apiFetch'
import type { ConversationListItem } from '../types'

export function useConversations() {
  const [items, setItems] = useState<ConversationListItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const refresh = useCallback(async () => {
    try {
      const list = await apiJson<ConversationListItem[]>('/api/conversations')
      setItems(list)
      setError(null)
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        setItems([])
      } else {
        setError(err instanceof Error ? err.message : 'Failed to load conversations')
      }
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    refresh()
  }, [refresh])

  const remove = useCallback(async (id: string) => {
    // Optimistic
    setItems(prev => prev.filter(c => c.id !== id))
    try {
      await apiFetch(`/api/conversations/${id}`, { method: 'DELETE' })
    } catch {
      // Refetch to repair the optimistic update on failure.
      refresh()
    }
  }, [refresh])

  return { items, loading, error, refresh, remove }
}
