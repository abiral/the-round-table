import { useEffect, useRef } from 'react'
import { Bot, AlertTriangle, RotateCw } from 'lucide-react'
import type { ChatMessage } from '../../types'
import { MessageBubble } from './MessageBubble'

interface ChatWindowProps {
  messages: ChatMessage[]
  isStreaming: boolean
  userFirstname?: string
  errored?: boolean
  errorMessage?: string | null
  onRetry?: () => void
  /** Increments when a conversation is bulk-loaded; signals "jump to top". */
  loadKey?: number
}

export function ChatWindow({
  messages,
  isStreaming,
  userFirstname,
  errored,
  errorMessage,
  onRetry,
  loadKey,
}: ChatWindowProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const bottomRef = useRef<HTMLDivElement>(null)
  const lastLoadKey = useRef<number | undefined>(loadKey)

  useEffect(() => {
    // A fresh bulk-load: jump to the top so the user sees their original
    // problem at the start of the conversation.
    if (loadKey !== undefined && loadKey !== lastLoadKey.current) {
      lastLoadKey.current = loadKey
      containerRef.current?.scrollTo({ top: 0 })
      return
    }
    // Incremental append (streaming, user reply, retry): follow the bottom.
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, errored, loadKey])

  const anyStreaming = messages.some(m => m.kind === 'agent' && m.isStreaming)

  return (
    <div ref={containerRef} className="flex-1 overflow-y-auto px-4 py-4">
      <div className="max-w-3xl mx-auto">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
            <div className="size-12 rounded-2xl bg-primary-soft text-primary-600 grid place-items-center mb-3">
              <Bot className="size-6" />
            </div>
            <h2 className="text-2xl font-semibold tracking-tight text-text-strong">
              {userFirstname ? `Hello, ${userFirstname}` : 'Hello'}
            </h2>
            <p className="text-sm text-text-muted mt-1 max-w-sm">
              Describe a technical problem and a panel of expert AI agents will
              brainstorm it together, turn by turn.
            </p>
          </div>
        )}

        {messages.map(msg => (
          <MessageBubble key={msg.id} message={msg} />
        ))}

        {/* Loading dots: streaming but no agent has started outputting yet */}
        {isStreaming && !anyStreaming && (
          <div className="flex gap-1.5 px-2 py-3">
            <span className="w-2 h-2 rounded-full bg-text-subtle animate-bounce [animation-delay:0s]" />
            <span className="w-2 h-2 rounded-full bg-text-subtle animate-bounce [animation-delay:0.15s]" />
            <span className="w-2 h-2 rounded-full bg-text-subtle animate-bounce [animation-delay:0.3s]" />
          </div>
        )}

        {/* Retry card: shown below the last message when the previous turn errored */}
        {errored && onRetry && (
          <div className="mt-2 mb-4 rounded-xl-soft border border-rose-200 bg-rose-50/60 px-4 py-3 flex items-start gap-3">
            <AlertTriangle className="size-4 text-rose-600 mt-0.5 flex-shrink-0" />
            <div className="flex-1 min-w-0">
              <div className="text-sm font-semibold text-rose-800">
                Conversation interrupted
              </div>
              <div className="text-xs text-rose-700/80 mt-0.5">
                {errorMessage || 'The previous turn did not complete.'}
              </div>
            </div>
            <button
              type="button"
              onClick={onRetry}
              className="inline-flex items-center gap-1.5 h-8 px-3 rounded-full
                         bg-white border border-rose-200 text-rose-700 text-xs font-semibold
                         hover:bg-rose-100 transition-colors flex-shrink-0"
            >
              <RotateCw className="size-3.5" />
              Continue
            </button>
          </div>
        )}

        <div ref={bottomRef} />
      </div>
    </div>
  )
}
