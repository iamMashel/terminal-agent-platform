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
}

export interface ChatMessage {
  id: number
  role: 'user' | 'assistant'
  content: string
  commands?: CommandProposal[]
}
