import { useState, useRef, type KeyboardEvent, type ChangeEvent } from 'react'
import { ArrowUp, Sparkles, Square } from 'lucide-react'
import type { Phase } from '../../types'

interface InputBarProps {
  onSubmit: (content: string) => void
  onCancel: () => void
  phase: Phase
  placeholder?: string
}

export function InputBar({ onSubmit, onCancel, phase, placeholder }: InputBarProps) {
  const [value, setValue] = useState('')
  const ref = useRef<HTMLTextAreaElement>(null)

  const isStreaming = phase === 'streaming'
  const disabled = isStreaming

  function handleSubmit() {
    const trimmed = value.trim()
    if (!trimmed || disabled) return
    onSubmit(trimmed)
    setValue('')
    if (ref.current) ref.current.style.height = 'auto'
    ref.current?.focus()
  }

  function handleKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  function handleChange(e: ChangeEvent<HTMLTextAreaElement>) {
    setValue(e.target.value)
    const el = e.target
    el.style.height = 'auto'
    el.style.height = `${Math.min(el.scrollHeight, 200)}px`
  }

  const effectivePlaceholder = placeholder
    ?? (phase === 'awaiting_user'
      ? 'Reply to the moderator…'
      : 'Describe your problem or idea…')

  return (
    <div className="px-4 pb-4 pt-2 flex-shrink-0">
      <div className="max-w-3xl mx-auto">
        <div className="rounded-xl-soft border border-subtle bg-surface shadow-card px-5 pt-4 pb-3">
          <textarea
            ref={ref}
            value={value}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            disabled={disabled}
            rows={1}
            placeholder={effectivePlaceholder}
            className="w-full bg-transparent resize-none outline-none text-sm leading-relaxed
                       placeholder:text-text-subtle text-text-default
                       disabled:opacity-60 disabled:cursor-not-allowed min-h-[44px]"
          />
          <div className="flex items-center justify-between mt-1">
            <div className="flex gap-2">
              <div className="inline-flex items-center gap-1.5 h-8 px-3 rounded-full
                              bg-primary-soft text-primary-600 text-xs font-medium
                              border border-transparent">
                <Sparkles className="size-3.5" />
                Brainstorm
              </div>
            </div>

            {isStreaming ? (
              <button
                type="button"
                onClick={onCancel}
                title="Stop"
                className="size-10 rounded-full grid place-items-center
                           bg-rose-50 text-rose-600 hover:bg-rose-100 transition-colors"
              >
                <Square className="size-4" />
              </button>
            ) : (
              <button
                type="button"
                onClick={handleSubmit}
                disabled={!value.trim()}
                title="Send (Enter)"
                className="size-10 rounded-full grid place-items-center text-white
                           bg-primary-gradient shadow-pop
                           hover:brightness-105 active:brightness-95
                           disabled:opacity-40 disabled:shadow-none disabled:cursor-not-allowed
                           transition"
              >
                <ArrowUp className="size-5" />
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
