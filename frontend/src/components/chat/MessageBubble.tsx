import { AGENT_CONFIG } from '../../types'
import type { ChatMessage } from '../../types'
import { AgentBadge } from './AgentBadge'
import { MarkdownContent } from './MarkdownContent'
import { cn } from '../../lib/utils'

interface MessageBubbleProps {
  message: ChatMessage
}

export function MessageBubble({ message }: MessageBubbleProps) {
  if (message.kind === 'user') {
    return (
      <div className="flex justify-end mb-4">
        <div className="max-w-[72%] bg-primary-500 text-white rounded-xl-soft rounded-tr-md px-4 py-3 shadow-card">
          <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
        </div>
      </div>
    )
  }

  const { agent, role, content, isStreaming, provider, isChirp } = message
  const isMarcusIntake = role === 'intake'
  const isMarcusSummary = role === 'summary'
  const isMarcusConclude = role === 'conclude'
  const cfg = AGENT_CONFIG[agent] ?? { border: 'border-subtle', bgColor: '', color: '' }

  if (isMarcusIntake || isMarcusSummary || isMarcusConclude) {
    return (
      <div className="mb-4">
        <div className="bg-primary-soft border border-indigo-200 rounded-xl-soft px-5 py-4 shadow-card">
          <AgentBadge agentName={agent} role={role} provider={provider} />
          <div className="mt-1 text-text-default">
            <MarkdownContent content={content} isStreaming={isStreaming} />
          </div>
        </div>
      </div>
    )
  }

  if (isChirp) {
    return (
      <div className="flex justify-start mb-3">
        <div className="max-w-[70%] ml-10">
          <AgentBadge agentName={agent} role={role} provider={provider} />
          <div
            className={cn(
              'border-l-2 pl-3 py-1 text-sm italic text-text-muted',
              isStreaming ? cfg.border : 'border-subtle'
            )}
          >
            <MarkdownContent content={content} isStreaming={isStreaming} />
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex justify-start mb-4">
      <div className="max-w-[78%]">
        <AgentBadge agentName={agent} role={role} provider={provider} />
        <div
          className={cn(
            'bg-surface border rounded-xl-soft rounded-tl-md px-4 py-3 shadow-card text-text-default',
            isStreaming ? cfg.border : 'border-subtle'
          )}
        >
          <MarkdownContent content={content} isStreaming={isStreaming} />
        </div>
      </div>
    </div>
  )
}
