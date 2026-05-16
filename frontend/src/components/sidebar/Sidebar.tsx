import { Bot, LogOut, X } from 'lucide-react'
import type { ConversationListItem } from '../../types'
import type { AuthUser } from '../../hooks/useAuth'
import { groupByBucket } from '../../lib/timeBuckets'
import { cn } from '../../lib/utils'
import { NewChatButton } from './NewChatButton'
import { TimeBucketHeader } from './TimeBucketHeader'
import { ConversationItem } from './ConversationItem'

interface SidebarProps {
  user: AuthUser
  conversations: ConversationListItem[]
  loading: boolean
  activeId: string | null
  mobileOpen: boolean
  onMobileClose: () => void
  onNew: () => void
  onSelect: (id: string) => void
  onDelete: (id: string) => void
  onLogout: () => void
}

export function Sidebar({
  user,
  conversations,
  loading,
  activeId,
  mobileOpen,
  onMobileClose,
  onNew,
  onSelect,
  onDelete,
  onLogout,
}: SidebarProps) {
  const grouped = groupByBucket(conversations, c => new Date(c.last_message_at))

  return (
    <>
      {/* Mobile backdrop */}
      {mobileOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/30 md:hidden"
          onClick={onMobileClose}
          aria-hidden="true"
        />
      )}

      <aside
        className={cn(
          'w-64 h-full flex flex-col bg-surface border-r border-subtle flex-shrink-0',
          // Drawer below md, in-flow at md and up.
          'fixed inset-y-0 left-0 z-40 transition-transform duration-200 ease-out',
          'md:relative md:translate-x-0 md:transition-none',
          mobileOpen ? 'translate-x-0' : '-translate-x-full',
        )}
        aria-hidden={!mobileOpen ? undefined : false}
      >
      {/* Brand */}
      <div className="px-4 py-4 flex items-center gap-2">
        <div className="size-8 rounded-xl bg-primary-soft text-primary-600 grid place-items-center">
          <Bot className="size-4" />
        </div>
        <span className="text-sm font-semibold text-text-strong tracking-tight">
          Brainstorm
        </span>
        <button
          type="button"
          onClick={onMobileClose}
          title="Close menu"
          className="ml-auto size-8 rounded-full grid place-items-center text-text-muted hover:bg-surface-muted md:hidden"
        >
          <X className="size-4" />
        </button>
      </div>

      {/* New chat */}
      <div className="px-3">
        <NewChatButton onClick={onNew} />
      </div>

      {/* Conversation list */}
      <div className="flex-1 overflow-y-auto px-3 mt-4">
        {loading && conversations.length === 0 && (
          <div className="text-xs text-text-subtle px-2 py-2">Loading…</div>
        )}
        {!loading && conversations.length === 0 && (
          <div className="text-xs text-text-subtle px-2 py-2">
            No conversations yet. Start a new chat to begin.
          </div>
        )}
        {grouped.map(({ bucket, items }) => (
          <div key={bucket}>
            <TimeBucketHeader label={bucket} />
            {items.map(item => (
              <ConversationItem
                key={item.id}
                item={item}
                active={item.id === activeId}
                onSelect={onSelect}
                onDelete={onDelete}
              />
            ))}
          </div>
        ))}
      </div>

      {/* User identity + logout */}
      <div className="border-t border-subtle px-3 py-3">
        <div className="flex items-center gap-2">
          <div className="size-8 rounded-full bg-surface-muted text-text-default grid place-items-center text-xs font-semibold">
            {user.firstname.slice(0, 1)}{user.lastname.slice(0, 1)}
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-sm font-semibold text-text-strong truncate">
              {user.firstname} {user.lastname}
            </div>
            <div className="text-[11px] text-text-subtle truncate">{user.email}</div>
          </div>
          <button
            type="button"
            onClick={onLogout}
            title="Sign out"
            className="size-8 rounded-full grid place-items-center text-text-muted hover:bg-surface-muted hover:text-text-strong transition-colors"
          >
            <LogOut className="size-4" />
          </button>
        </div>
      </div>
    </aside>
    </>
  )
}
