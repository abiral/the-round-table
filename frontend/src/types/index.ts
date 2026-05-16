export type StreamEventType =
  | 'session'
  | 'agent_start'
  | 'agent_chunk'
  | 'agent_done'
  | 'router_decision'
  | 'awaiting_user_input'
  | 'conclude_offered'
  | 'done'
  | 'error'

export interface StreamEvent {
  type: StreamEventType
  // session
  session_id?: string
  // agent_*
  agent?: string
  role?: string
  provider?: 'anthropic' | 'gemini'
  content?: string
  chirp?: boolean
  // router_decision
  action?: string
  next_speaker?: string | null
  reason?: string
  // awaiting_user_input
  summary?: string
  question?: string
  // conclude_offered
  exports_available?: ExportKind[]
  // done
  consensus_score?: number
  // error
  message?: string
}

export type AgentName =
  | 'Saugat Adhikari'
  | 'Nirajan Sharma'
  | 'Samriddhi Neupane'
  | 'Prakriti Bhandari'
  | 'Aayush Koirala'
  | 'Santosh Poudel'
  | 'Shreya Manandhar'
  | 'Rakesh Tandulkar'
  | 'Suvash BK'
  | 'Prem Nepali'
  | 'user'

export interface AgentMessage {
  id: string
  kind: 'agent'
  agent: AgentName
  role: string
  provider: 'anthropic' | 'gemini'
  content: string
  isStreaming: boolean
  isChirp: boolean
  timestamp: Date
}

export interface UserMessage {
  id: string
  kind: 'user'
  content: string
  timestamp: Date
}

export type ChatMessage = AgentMessage | UserMessage

export type Phase = 'idle' | 'streaming' | 'awaiting_user' | 'concluded'

export type ExportKind = 'pdf' | 'adr' | 'plan'

export type ConversationStatus = 'in_progress' | 'awaiting_user' | 'concluded'

export interface ConversationListItem {
  id: string
  title: string
  status: ConversationStatus
  last_message_at: string
}

export interface ConversationDetail {
  id: string
  title: string
  status: ConversationStatus
  last_message_at: string
  state: {
    user_goal?: string
    constraints?: string[]
    discussions?: Array<{
      agent: string
      role: string
      content: string
      timestamp: string
      is_chirp?: boolean
    }>
    user_inputs?: Array<{
      role: 'user'
      content: string
      timestamp: string
    }>
    awaiting_user_input?: boolean
    pause_summary?: string
    pause_question?: string
    conversation_concluded?: boolean
    final_summary?: string
    [key: string]: unknown
  }
}

export interface PausePrompt {
  summary: string
  question: string
}

export interface BrainstormSession {
  sessionId: string | null
  messages: ChatMessage[]
  phase: Phase
  pausePrompt: PausePrompt | null
  conclusionSummary: string | null
  exportsAvailable: ExportKind[]
  consensusScore: number | null
  error: string | null
}

export const AGENT_CONFIG: Record<string, { color: string; bgColor: string; initials: string; border: string }> = {
  'Saugat Adhikari':   { color: 'text-purple-700',   bgColor: 'bg-purple-100',   initials: 'SA', border: 'border-purple-200' },
  'Nirajan Sharma':    { color: 'text-blue-700',     bgColor: 'bg-blue-100',     initials: 'NS', border: 'border-blue-200' },
  'Samriddhi Neupane': { color: 'text-green-700',    bgColor: 'bg-green-100',    initials: 'SN', border: 'border-green-200' },
  'Prakriti Bhandari': { color: 'text-red-700',      bgColor: 'bg-red-100',      initials: 'PB', border: 'border-red-200' },
  'Aayush Koirala':    { color: 'text-orange-700',   bgColor: 'bg-orange-100',   initials: 'AK', border: 'border-orange-200' },
  'Santosh Poudel':    { color: 'text-indigo-700',   bgColor: 'bg-indigo-100',   initials: 'SP', border: 'border-indigo-200' },
  'Shreya Manandhar':  { color: 'text-pink-700',     bgColor: 'bg-pink-100',     initials: 'SM', border: 'border-pink-200' },
  'Rakesh Tandulkar':  { color: 'text-amber-700',    bgColor: 'bg-amber-100',    initials: 'RT', border: 'border-amber-200' },
  'Suvash BK':         { color: 'text-rose-700',     bgColor: 'bg-rose-100',     initials: 'SB', border: 'border-rose-200' },
  'Prem Nepali':       { color: 'text-teal-700',     bgColor: 'bg-teal-100',     initials: 'PN', border: 'border-teal-200' },
}
