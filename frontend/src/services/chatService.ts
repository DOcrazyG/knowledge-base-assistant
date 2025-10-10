import api from './api'

export interface ChatMessage {
  id?: string
  role: 'user' | 'assistant'
  content: string
  timestamp?: Date
}

export interface ChatRequest {
  message: string
  session_id?: string
}

export interface ChatResponse {
  answer: string
  session_id: string
}

export const chatService = {
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    const response = await api.post<ChatResponse>('/chat/completions', request)
    return response.data
  },
}