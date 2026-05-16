import { MessageCircleQuestion } from 'lucide-react'

interface PauseBannerProps {
  question: string
}

export function PauseBanner({ question }: PauseBannerProps) {
  return (
    <div className="mx-4 mb-2 flex-shrink-0">
      <div className="max-w-3xl mx-auto px-4 py-3 bg-primary-soft border border-indigo-200 rounded-xl flex items-start gap-3">
        <MessageCircleQuestion className="w-4 h-4 text-primary-500 mt-0.5 flex-shrink-0" />
        <div className="flex-1 text-sm text-text-strong">
          <span className="font-semibold">Moderator asks:</span>{' '}
          <span>{question}</span>
        </div>
      </div>
    </div>
  )
}
