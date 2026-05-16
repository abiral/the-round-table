import { AGENT_CONFIG } from '../../types'

interface AgentBadgeProps {
  agentName: string
  role?: string
  provider?: 'anthropic' | 'gemini'
}

export function AgentBadge({ agentName, role, provider }: AgentBadgeProps) {
  const cfg = AGENT_CONFIG[agentName] ?? {
    color: 'text-gray-700',
    bgColor: 'bg-gray-100',
    initials: agentName.slice(0, 2).toUpperCase(),
  }

  const roleLabel: Record<string, string> = {
    moderator: 'Moderator',
    intake: 'Moderator, Intake',
    summary: 'Moderator, Check-in',
    conclude: 'Moderator, Wrap-up',
    synthesizer: 'Synthesizer',
    ai_architect: 'AI Architect',
    fullstack: 'Full Stack Engineer',
    qa: 'QA Engineer',
    ml_scientist: 'ML Scientist',
    php_plugin: 'WordPress Plugin Developer',
    php_theme: 'WordPress Theme Developer',
    wp_theme_reviewer: 'WP Theme Reviewer',
    wp_plugin_reviewer: 'WP Plugin Reviewer',
    ux_engineer: 'UI / UX Engineer',
  }

  return (
    <div className="flex items-center gap-2 mb-1.5">
      <div
        className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0 ${cfg.bgColor} ${cfg.color}`}
      >
        {cfg.initials}
      </div>
      <div className="flex flex-col leading-tight">
        <div className="flex items-center gap-1.5">
          <span className={`text-sm font-semibold ${cfg.color}`}>{agentName}</span>
          {provider && (
            <span className={`text-[10px] font-medium px-1.5 py-0.5 rounded-full ${
              provider === 'gemini'
                ? 'bg-blue-50 text-blue-500 border border-blue-200'
                : 'bg-orange-50 text-orange-500 border border-orange-200'
            }`}>
              {provider === 'gemini' ? 'Gemini' : 'Claude'}
            </span>
          )}
        </div>
        {role && (
          <span className="text-[11px] text-gray-400 capitalize">
            {roleLabel[role] ?? role}
          </span>
        )}
      </div>
    </div>
  )
}
