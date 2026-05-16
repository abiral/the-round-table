import { useCallback, useState } from 'react'
import { Menu } from 'lucide-react'
import { ChatWindow } from './components/chat/ChatWindow'
import { InputBar } from './components/chat/InputBar'
import { PauseBanner } from './components/chat/PauseBanner'
import { ExportPanel } from './components/chat/ExportPanel'
import { LoginScreen } from './components/auth/LoginScreen'
import { Sidebar } from './components/sidebar/Sidebar'
import { useBrainstorm } from './hooks/useBrainstorm'
import { useAuth, type AuthUser } from './hooks/useAuth'
import { useConversations } from './hooks/useConversations'

export default function App() {
  const auth = useAuth()

  if (auth.loading) {
    return (
      <div className="min-h-full grid place-items-center bg-app-gradient">
        <div className="flex gap-1.5">
          <span className="w-2 h-2 rounded-full bg-text-subtle animate-bounce [animation-delay:0s]" />
          <span className="w-2 h-2 rounded-full bg-text-subtle animate-bounce [animation-delay:0.15s]" />
          <span className="w-2 h-2 rounded-full bg-text-subtle animate-bounce [animation-delay:0.3s]" />
        </div>
      </div>
    )
  }

  if (!auth.user) {
    return <LoginScreen onLogin={auth.login} loading={auth.loading} />
  }

  return <BrainstormApp user={auth.user} onLogout={auth.logout} />
}

function BrainstormApp({ user, onLogout }: { user: AuthUser; onLogout: () => Promise<void> }) {
  const conversations = useConversations()
  const [mobileOpen, setMobileOpen] = useState(false)

  const closeMobile = useCallback(() => setMobileOpen(false), [])

  const onSaved = useCallback(() => {
    conversations.refresh()
  }, [conversations])

  const brainstorm = useBrainstorm({ onSaved })
  const { session, submitProblem, sendUserReply, downloadExport, cancel, reset, loadConversation } = brainstorm
  const { phase, pausePrompt, exportsAvailable, sessionId } = session

  function handleSubmit(text: string) {
    if (phase === 'awaiting_user') {
      sendUserReply(text)
    } else if (phase === 'idle') {
      submitProblem(text)
    }
  }

  const isStreaming = phase === 'streaming'
  const isConcluded = phase === 'concluded'

  return (
    <div className="flex h-full bg-app-gradient">
      <Sidebar
        user={user}
        conversations={conversations.items}
        loading={conversations.loading}
        activeId={sessionId}
        mobileOpen={mobileOpen}
        onMobileClose={closeMobile}
        onNew={() => { reset(); closeMobile() }}
        onSelect={(id) => { void loadConversation(id); closeMobile() }}
        onDelete={(id) => {
          conversations.remove(id)
          if (id === sessionId) reset()
        }}
        onLogout={onLogout}
      />

      <main className="flex-1 flex flex-col min-w-0">
        {/* Slim status strip */}
        <div className="h-12 px-4 md:px-6 flex items-center justify-between flex-shrink-0">
          <button
            type="button"
            onClick={() => setMobileOpen(true)}
            title="Open menu"
            className="md:hidden size-9 rounded-full grid place-items-center text-text-muted hover:bg-surface/60 transition-colors"
          >
            <Menu className="size-5" />
          </button>
          <div className="ml-auto flex items-center">
          {phase === 'awaiting_user' && (
            <div className="text-xs font-semibold text-primary-600 bg-primary-soft border border-indigo-200 px-3 py-1.5 rounded-full">
              Waiting for your input
            </div>
          )}
          {isConcluded && (
            <div className="text-xs font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 px-3 py-1.5 rounded-full">
              Concluded
            </div>
          )}
          </div>
        </div>

        <ChatWindow
          messages={session.messages}
          isStreaming={isStreaming}
          userFirstname={user.firstname}
        />

        {session.error && (
          <div className="mx-4 mb-2 px-4 py-2 bg-rose-50 border border-rose-200 rounded-lg text-sm text-rose-700 flex-shrink-0">
            {session.error}
          </div>
        )}

        {phase === 'awaiting_user' && pausePrompt?.question && (
          <PauseBanner question={pausePrompt.question} />
        )}

        {isConcluded ? (
          <ExportPanel
            available={exportsAvailable}
            onDownload={downloadExport}
            onReset={reset}
          />
        ) : (
          <InputBar
            onSubmit={handleSubmit}
            onCancel={cancel}
            phase={phase}
          />
        )}
      </main>
    </div>
  )
}
