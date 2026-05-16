import { useState, useCallback, useRef } from 'react'
import type {
  AgentMessage,
  BrainstormSession,
  ChatMessage,
  ConversationDetail,
  ExportKind,
  StreamEvent,
  UserMessage,
} from '../types'
import { apiFetch, apiJson } from '../lib/apiFetch'

function uid(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2)}`
}

const INITIAL_SESSION: BrainstormSession = {
  sessionId: null,
  messages: [],
  phase: 'idle',
  pausePrompt: null,
  conclusionSummary: null,
  exportsAvailable: [],
  consensusScore: null,
  error: null,
}

export interface UseBrainstormOptions {
  onSaved?: () => void
}

export function useBrainstorm(options: UseBrainstormOptions = {}) {
  const [session, setSession] = useState<BrainstormSession>(INITIAL_SESSION)
  const abortRef = useRef<AbortController | null>(null)
  const sessionIdRef = useRef<string | null>(null)
  const onSavedRef = useRef(options.onSaved)
  onSavedRef.current = options.onSaved

  // ── Mutators ──────────────────────────────────────────────────────────

  const addAgentMessage = useCallback((
    agent: string,
    role: string,
    provider: 'anthropic' | 'gemini',
    isChirp: boolean,
  ) => {
    setSession(prev => ({
      ...prev,
      messages: [
        ...prev.messages,
        {
          id: uid(),
          kind: 'agent',
          agent: agent as AgentMessage['agent'],
          role,
          provider,
          content: '',
          isStreaming: true,
          isChirp,
          timestamp: new Date(),
        },
      ],
    }))
  }, [])

  const appendChunk = useCallback((agentName: string, chunk: string) => {
    setSession(prev => {
      const msgs = [...prev.messages]
      const idx = msgs.findLastIndex(
        m => m.kind === 'agent' && m.agent === agentName && m.isStreaming
      )
      if (idx === -1) return prev
      const m = msgs[idx] as AgentMessage
      msgs[idx] = { ...m, content: m.content + chunk }
      return { ...prev, messages: msgs }
    })
  }, [])

  const finishAgent = useCallback((agentName: string) => {
    setSession(prev => ({
      ...prev,
      messages: prev.messages.map(m =>
        m.kind === 'agent' && m.agent === agentName && m.isStreaming
          ? { ...m, isStreaming: false }
          : m
      ),
    }))
  }, [])

  const appendUserMessage = useCallback((content: string) => {
    const msg: UserMessage = {
      id: uid(),
      kind: 'user',
      content,
      timestamp: new Date(),
    }
    setSession(prev => ({
      ...prev,
      messages: [...prev.messages, msg],
    }))
  }, [])

  // ── SSE consumption (shared between submit + respond) ─────────────────

  const consumeSSE = useCallback(async (response: Response) => {
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    if (!response.body) throw new Error('No response body')

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const parts = buffer.split('\n\n')
      buffer = parts.pop() ?? ''

      for (const part of parts) {
        if (!part.startsWith('data: ')) continue
        const json = part.slice(6).trim()
        if (!json) continue

        let event: StreamEvent
        try { event = JSON.parse(json) } catch { continue }

        switch (event.type) {
          case 'session':
            if (event.session_id) {
              sessionIdRef.current = event.session_id
              setSession(prev => ({ ...prev, sessionId: event.session_id! }))
            }
            break
          case 'agent_start':
            addAgentMessage(
              event.agent!,
              event.role!,
              event.provider ?? 'anthropic',
              !!event.chirp,
            )
            break
          case 'agent_chunk':
            appendChunk(event.agent!, event.content!)
            break
          case 'agent_done':
            finishAgent(event.agent!)
            break
          case 'router_decision':
            // Debug-only; ignored in UI for now.
            break
          case 'awaiting_user_input':
            setSession(prev => ({
              ...prev,
              phase: 'awaiting_user',
              pausePrompt: {
                summary: event.summary ?? '',
                question: event.question ?? '',
              },
            }))
            break
          case 'conclude_offered':
            setSession(prev => ({
              ...prev,
              phase: 'concluded',
              conclusionSummary: event.summary ?? null,
              exportsAvailable: event.exports_available ?? ['pdf', 'adr', 'plan'],
            }))
            break
          case 'done':
            setSession(prev =>
              // Don't downgrade from awaiting_user / concluded back to idle.
              prev.phase === 'streaming'
                ? { ...prev, phase: 'idle' }
                : prev
            )
            // Backend has finished persisting; let the sidebar refresh.
            onSavedRef.current?.()
            break
          case 'error':
            setSession(prev => ({
              ...prev,
              phase: 'idle',
              error: event.message ?? 'An error occurred',
            }))
            break
        }
      }
    }
  }, [addAgentMessage, appendChunk, finishAgent])

  // ── Public actions ────────────────────────────────────────────────────

  const submitProblem = useCallback(async (problem: string) => {
    abortRef.current?.abort()
    const controller = new AbortController()
    abortRef.current = controller
    sessionIdRef.current = null

    setSession({
      ...INITIAL_SESSION,
      messages: [
        { id: uid(), kind: 'user', content: problem, timestamp: new Date() },
      ],
      phase: 'streaming',
    })

    try {
      const res = await apiFetch('/api/brainstorm', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ problem }),
        signal: controller.signal,
      })
      await consumeSSE(res)
    } catch (err: unknown) {
      if (err instanceof Error && err.name === 'AbortError') return
      setSession(prev => ({
        ...prev,
        phase: 'idle',
        error: err instanceof Error ? err.message : 'Unknown error',
      }))
    }
  }, [consumeSSE])

  const sendUserReply = useCallback(async (content: string) => {
    const sid = sessionIdRef.current
    if (!sid) {
      setSession(prev => ({ ...prev, error: 'No active session' }))
      return
    }

    abortRef.current?.abort()
    const controller = new AbortController()
    abortRef.current = controller

    appendUserMessage(content)
    setSession(prev => ({
      ...prev,
      phase: 'streaming',
      pausePrompt: null,
    }))

    try {
      const res = await apiFetch(`/api/brainstorm/${sid}/respond`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content }),
        signal: controller.signal,
      })
      await consumeSSE(res)
    } catch (err: unknown) {
      if (err instanceof Error && err.name === 'AbortError') return
      setSession(prev => ({
        ...prev,
        phase: 'idle',
        error: err instanceof Error ? err.message : 'Unknown error',
      }))
    }
  }, [consumeSSE, appendUserMessage])

  const downloadExport = useCallback(async (kind: ExportKind) => {
    const sid = sessionIdRef.current
    if (!sid) return

    const res = await apiFetch(`/api/brainstorm/${sid}/export/${kind}`)
    if (!res.ok) {
      setSession(prev => ({ ...prev, error: `Export failed (HTTP ${res.status})` }))
      return
    }

    const blob = await res.blob()
    const url = URL.createObjectURL(blob)
    const filename = kind === 'pdf'
      ? 'brainstorm-report.pdf'
      : kind === 'adr'
        ? 'decision-record.md'
        : 'plan.md'

    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(url)
  }, [])

  const cancel = useCallback(() => {
    abortRef.current?.abort()
    setSession(prev => ({ ...prev, phase: 'idle' }))
  }, [])

  const reset = useCallback(() => {
    abortRef.current?.abort()
    sessionIdRef.current = null
    setSession(INITIAL_SESSION)
  }, [])

  /**
   * Rehydrate a saved conversation into the chat surface.
   * Discussions and user inputs are woven together by timestamp; phase is
   * derived from the persisted status so the right banner / panel renders.
   */
  const loadConversation = useCallback(async (conversationId: string) => {
    abortRef.current?.abort()
    sessionIdRef.current = conversationId

    setSession({
      ...INITIAL_SESSION,
      sessionId: conversationId,
      phase: 'idle',
      messages: [],
    })

    let detail: ConversationDetail
    try {
      detail = await apiJson<ConversationDetail>(`/api/conversations/${conversationId}`)
    } catch (err) {
      setSession(prev => ({
        ...prev,
        error: err instanceof Error ? err.message : 'Failed to load conversation',
      }))
      return
    }

    const state = detail.state ?? {}
    const discussions = state.discussions ?? []
    const userInputs = state.user_inputs ?? []

    type TimelineEntry =
      | { ts: string; kind: 'agent'; data: NonNullable<typeof state.discussions>[number] }
      | { ts: string; kind: 'user'; data: NonNullable<typeof state.user_inputs>[number] }

    const timeline: TimelineEntry[] = [
      ...discussions.map(d => ({ ts: d.timestamp, kind: 'agent' as const, data: d })),
      ...userInputs.map(u => ({ ts: u.timestamp, kind: 'user' as const, data: u })),
    ]
    timeline.sort((a, b) => a.ts.localeCompare(b.ts))

    const messages: ChatMessage[] = timeline.map(entry => {
      if (entry.kind === 'user') {
        return {
          id: uid(),
          kind: 'user',
          content: entry.data.content,
          timestamp: new Date(entry.data.timestamp),
        } satisfies UserMessage
      }
      const d = entry.data
      return {
        id: uid(),
        kind: 'agent',
        agent: d.agent as AgentMessage['agent'],
        role: d.role,
        provider: 'anthropic',
        content: d.content,
        isStreaming: false,
        isChirp: !!d.is_chirp,
        timestamp: new Date(d.timestamp),
      } satisfies AgentMessage
    })

    setSession({
      sessionId: conversationId,
      messages,
      phase:
        detail.status === 'awaiting_user' ? 'awaiting_user'
        : detail.status === 'concluded'   ? 'concluded'
        :                                   'idle',
      pausePrompt: detail.status === 'awaiting_user'
        ? { summary: state.pause_summary ?? '', question: state.pause_question ?? '' }
        : null,
      conclusionSummary: detail.status === 'concluded' ? (state.final_summary ?? null) : null,
      exportsAvailable: detail.status === 'concluded' ? ['pdf', 'adr', 'plan'] : [],
      consensusScore: null,
      error: null,
    })
  }, [])

  const newConversation = useCallback(() => {
    reset()
  }, [reset])

  return {
    session,
    submitProblem,
    sendUserReply,
    downloadExport,
    cancel,
    reset,
    loadConversation,
    newConversation,
  }
}

export type UseBrainstormReturn = ReturnType<typeof useBrainstorm>

// Re-export for components that just want the type bag.
export type { ChatMessage }
