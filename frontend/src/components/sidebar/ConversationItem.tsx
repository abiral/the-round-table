import { MessageSquare, MessageCircleQuestion, CheckCircle2, Trash2 } from 'lucide-react'
import type { ConversationListItem, ConversationStatus } from '../../types'
import { cn } from '../../lib/utils'

interface ConversationItemProps {
  item: ConversationListItem
  active: boolean
  onSelect: (id: string) => void
  onDelete: (id: string) => void
}

const STATUS_ICON: Record<ConversationStatus, typeof MessageSquare> = {
  in_progress:   MessageSquare,
  awaiting_user: MessageCircleQuestion,
  concluded:     CheckCircle2,
}

const STATUS_COLOR: Record<ConversationStatus, string> = {
  in_progress:   'text-text-subtle',
  awaiting_user: 'text-primary-500',
  concluded:     'text-emerald-600',
}

export function ConversationItem({ item, active, onSelect, onDelete }: ConversationItemProps) {
  const Icon = STATUS_ICON[item.status]

  return (
    <div
      onClick={() => onSelect(item.id)}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault()
          onSelect(item.id)
        }
      }}
      className={cn(
        'group flex items-center gap-2 pl-2 pr-1.5 py-2 rounded-lg cursor-pointer transition-colors',
        active
          ? 'bg-primary-soft text-primary-600'
          : 'text-text-default hover:bg-surface-muted',
      )}
    >
      <Icon
        className={cn(
          'size-4 shrink-0',
          active ? 'text-primary-500' : STATUS_COLOR[item.status],
        )}
      />
      <span className="text-sm flex-1 min-w-0 truncate leading-snug">
        {item.title || 'Untitled brainstorm'}
      </span>
      <button
        type="button"
        onClick={(e) => {
          e.stopPropagation()
          if (window.confirm('Delete this conversation?')) onDelete(item.id)
        }}
        title="Delete conversation"
        aria-label="Delete conversation"
        className="size-6 rounded grid place-items-center shrink-0
                   text-text-subtle/70 hover:text-rose-600 hover:bg-rose-50
                   focus:outline-none focus:ring-2 focus:ring-rose-300
                   transition"
      >
        <Trash2 className="size-3.5" />
      </button>
    </div>
  )
}
