export interface ChatRequest {
  session_id: string
  message: string
}

export interface ChatResponse {
  message: string
  commands: CommandProposal[]
}

export interface CommandProposal {
  id: string
  cmd: string
  risk: 'low' | 'medium' | 'high'
  explanation: string
  status: CommandStatus
  execution?: CommandExecutionResponse
}

export type CommandStatus = 'proposed' | 'approved' | 'rejected'

export type ApprovalDecision = 'approved' | 'rejected'

export interface CommandApprovalResponse {
  command_id: string
  status: CommandStatus
  message: string
}

export interface CommandExecutionResponse {
  command_id: string
  status: 'completed' | 'failed'
  exit_code: number
  output: string
}

export interface ChatMessage {
  id: number
  role: 'user' | 'assistant'
  content: string
  commands?: CommandProposal[]
}

export interface SessionCreateResponse {
  success: boolean
  data: {
    session_id: string
  }
}

export interface SessionListResponse {
  success: boolean
  data: SessionListItem[]
}

export interface SessionListItem {
  id: string
}

export interface SessionDetailResponse {
  success: boolean
  data: {
    messages: SessionMessage[]
    commands: SessionCommand[]
  }
}

export interface SessionMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface SessionCommand {
  id: string
  cmd: string
  risk: 'low' | 'medium' | 'high'
  status: CommandStatus
  output: string | null
}
