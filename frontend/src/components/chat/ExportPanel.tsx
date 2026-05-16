import { useState } from 'react'
import { FileDown, FileText, FileCode, RotateCcw } from 'lucide-react'
import type { ExportKind } from '../../types'

interface ExportPanelProps {
  available: ExportKind[]
  onDownload: (kind: ExportKind) => Promise<void>
  onReset: () => void
}

const META: Record<ExportKind, { label: string; description: string; icon: typeof FileDown }> = {
  pdf:  { label: 'PDF Report',        description: 'Decision, rationale, and discussion trail', icon: FileDown },
  adr:  { label: 'Decision Record',   description: 'MADR-format ADR.md',                        icon: FileText },
  plan: { label: 'Plan for an Agent', description: 'Editor-ready plan.md',                      icon: FileCode },
}

export function ExportPanel({ available, onDownload, onReset }: ExportPanelProps) {
  const [pending, setPending] = useState<ExportKind | null>(null)

  async function handle(kind: ExportKind) {
    setPending(kind)
    try {
      await onDownload(kind)
    } finally {
      setPending(null)
    }
  }

  return (
    <div className="px-4 pb-4 pt-2 flex-shrink-0">
      <div className="max-w-3xl mx-auto rounded-xl-soft border border-subtle bg-surface shadow-card p-4">
        <div className="mb-3 flex items-center justify-between">
          <p className="text-sm font-semibold text-text-strong">
            Conversation concluded, export the outcome
          </p>
          <button
            type="button"
            onClick={onReset}
            className="text-xs text-text-muted hover:text-text-strong flex items-center gap-1 transition-colors"
          >
            <RotateCcw className="w-3 h-3" />
            Start a new session
          </button>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
          {available.map(kind => {
            const m = META[kind]
            const Icon = m.icon
            const isPending = pending === kind
            return (
              <button
                key={kind}
                type="button"
                onClick={() => handle(kind)}
                disabled={pending !== null}
                className="flex items-start gap-3 text-left p-3 rounded-xl
                           border border-subtle bg-surface
                           hover:border-strong hover:shadow-card hover:-translate-y-px transition-all
                           disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:translate-y-0"
              >
                <span className="size-8 rounded-full bg-primary-soft text-primary-600 grid place-items-center mt-0.5 flex-shrink-0">
                  <Icon className="w-4 h-4" />
                </span>
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-semibold text-text-strong">
                    {isPending ? 'Preparing…' : m.label}
                  </div>
                  <div className="text-xs text-text-muted mt-0.5">{m.description}</div>
                </div>
              </button>
            )
          })}
        </div>
      </div>
    </div>
  )
}
