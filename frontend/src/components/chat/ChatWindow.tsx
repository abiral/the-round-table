import { useEffect, useRef } from 'react'
import { Bot } from 'lucide-react'
import type { ChatMessage } from '../../types'
import { MessageBubble } from './MessageBubble'

interface ChatWindowProps {
  messages: ChatMessage[]
  isStreaming: boolean
  userFirstname?: string
}

export function ChatWindow({ messages, isStreaming, userFirstname }: ChatWindowProps) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const anyStreaming = messages.some(m => m.kind === 'agent' && m.isStreaming)

  return (
    <div className="flex-1 overflow-y-auto px-4 py-4">
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

        <div ref={bottomRef} />
      </div>
    </div>
  )
}
