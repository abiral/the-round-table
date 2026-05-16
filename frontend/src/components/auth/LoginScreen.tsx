import { useState, type FormEvent } from 'react'
import { Bot } from 'lucide-react'

interface LoginScreenProps {
  onLogin: (email: string, password: string) => Promise<void>
  loading: boolean
}

export function LoginScreen({ onLogin, loading }: LoginScreenProps) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    if (!email.trim() || !password) return
    setError(null)
    setSubmitting(true)
    try {
      await onLogin(email.trim(), password)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Sign in failed')
    } finally {
      setSubmitting(false)
    }
  }

  const disabled = submitting || loading || !email.trim() || !password

  return (
    <div className="min-h-full grid place-items-center bg-gradient-to-br from-[#FBF7F3] to-[#F4F2FD] px-4 py-12">
      <div className="w-full max-w-sm">
        <div className="flex flex-col items-center mb-6">
          <div className="size-12 rounded-2xl bg-indigo-100 text-indigo-700 grid place-items-center mb-3">
            <Bot className="size-6" />
          </div>
          <h1 className="text-xl font-semibold text-gray-900 tracking-tight">
            Welcome back
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            Sign in to continue your brainstorm.
          </p>
        </div>

        <form
          onSubmit={handleSubmit}
          className="rounded-2xl border border-gray-200 bg-white shadow-sm px-6 py-6 space-y-4"
        >
          <div className="space-y-1.5">
            <label htmlFor="email" className="text-xs font-semibold text-gray-700">
              Email
            </label>
            <input
              id="email"
              type="email"
              autoComplete="email"
              required
              value={email}
              onChange={e => setEmail(e.target.value)}
              className="w-full h-10 rounded-xl border border-gray-300 px-3 text-sm
                         focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder="you@example.com"
            />
          </div>

          <div className="space-y-1.5">
            <label htmlFor="password" className="text-xs font-semibold text-gray-700">
              Password
            </label>
            <input
              id="password"
              type="password"
              autoComplete="current-password"
              required
              value={password}
              onChange={e => setPassword(e.target.value)}
              className="w-full h-10 rounded-xl border border-gray-300 px-3 text-sm
                         focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder="••••••••"
            />
          </div>

          {error && (
            <div className="text-xs px-3 py-2 bg-rose-50 border border-rose-200 text-rose-700 rounded-lg">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={disabled}
            className="w-full h-10 rounded-xl bg-indigo-600 text-white text-sm font-semibold
                       shadow-[0_6px_16px_rgba(99,102,241,0.25)]
                       hover:bg-indigo-700 active:bg-indigo-800
                       disabled:opacity-50 disabled:cursor-not-allowed disabled:shadow-none
                       transition-colors"
          >
            {submitting ? 'Signing in…' : 'Sign in'}
          </button>

          <p className="text-[11px] text-gray-400 text-center">
            New accounts are created by an admin. Ask one of them to onboard you.
          </p>
        </form>
      </div>
    </div>
  )
}
