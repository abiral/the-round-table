import { Plus } from 'lucide-react'

interface NewChatButtonProps {
  onClick: () => void
}

export function NewChatButton({ onClick }: NewChatButtonProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="w-full flex items-center justify-center gap-2 h-10 px-3 rounded-full
                 bg-primary-500 text-white text-sm font-semibold
                 shadow-pop hover:bg-primary-600 active:bg-primary-600
                 transition-colors"
    >
      <Plus className="size-4" />
      New Chat
    </button>
  )
}
