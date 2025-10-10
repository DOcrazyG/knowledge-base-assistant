import React, { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import { useAuth } from '../hooks/useAuth'
import { chatService, ChatMessage, ChatRequest } from '../services/chatService'
import { fileService } from '../services/fileService'

const Chat: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: 'assistant',
      content: 'Hello! I am your Knowledge Base Assistant. How can I help you today?',
      timestamp: new Date(),
    }
  ])
  const [inputValue, setInputValue] = useState('')
  const [loading, setLoading] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [uploadStatus, setUploadStatus] = useState<{ loading: boolean; message: string } | null>(null)
  
  const { logout } = useAuth()
  const navigate = useNavigate()
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleLogout = () => {
    logout()
    navigate('/login', { replace: true })
  }

  const handleSend = async () => {
    if (!inputValue.trim() || loading) return

    // Add user message to chat
    const userMessage: ChatMessage = {
      role: 'user',
      content: inputValue,
      timestamp: new Date(),
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setLoading(true)

    try {
      const request: ChatRequest = {
        message: inputValue,
      }

      const response = await chatService.sendMessage(request)
      
      // Add assistant message to chat
      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.answer,
        timestamp: new Date(),
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('Error sending message:', error)
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0])
    }
  }

  const handleFileUpload = async () => {
    if (!selectedFile) return

    setUploadStatus({ loading: true, message: 'Uploading file...' })

    try {
      await fileService.uploadFile(selectedFile)
      setUploadStatus({ loading: false, message: 'File uploaded successfully!' })
      setSelectedFile(null)
      
      // Clear status after 3 seconds
      setTimeout(() => setUploadStatus(null), 3000)
    } catch (error) {
      console.error('Error uploading file:', error)
      setUploadStatus({ loading: false, message: 'Failed to upload file.' })
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex flex-col h-screen bg-white">
      {/* Header */}
      <header className="bg-indigo-600 text-white p-4 shadow">
        <div className="container mx-auto flex justify-between items-center">
          <h1 className="text-xl font-bold">Knowledge Base Assistant</h1>
          <button
            onClick={handleLogout}
            className="px-4 py-2 text-sm bg-white text-indigo-600 rounded hover:bg-indigo-50 transition"
          >
            Logout
          </button>
        </div>
      </header>

      {/* Chat Container */}
      <div className="flex-1 overflow-hidden flex flex-col">
        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
          <div className="max-w-4xl mx-auto space-y-6">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-lg p-4 ${
                    message.role === 'user'
                      ? 'bg-indigo-500 text-white'
                      : 'bg-white border border-gray-200'
                  }`}
                >
                  {message.role === 'assistant' ? (
                    <div className="prose prose-indigo max-w-none">
                      <ReactMarkdown
                        components={{
                          a: ({node, ...props}) => <a className="text-blue-600 hover:underline" {...props} />,
                          code: ({node, className, children, ...props}) => (
                            <code className={`bg-gray-100 rounded p-1 ${className}`} {...props}>
                              {children}
                            </code>
                          ),
                          pre: ({node, children, ...props}) => (
                            <pre className="bg-gray-800 text-white p-4 rounded overflow-x-auto" {...props}>
                              {children}
                            </pre>
                          ),
                          ul: ({node, children, ...props}) => (
                            <ul className="list-disc pl-5" {...props}>
                              {children}
                            </ul>
                          ),
                          ol: ({node, children, ...props}) => (
                            <ol className="list-decimal pl-5" {...props}>
                              {children}
                            </ol>
                          ),
                          li: ({node, children, ...props}) => (
                            <li className="mb-1" {...props}>
                              {children}
                            </li>
                          ),
                          blockquote: ({node, children, ...props}) => (
                            <blockquote className="border-l-4 border-gray-300 pl-4 italic" {...props}>
                              {children}
                            </blockquote>
                          ),
                          h1: ({node, children, ...props}) => (
                            <h1 className="text-2xl font-bold mt-4 mb-2" {...props}>
                              {children}
                            </h1>
                          ),
                          h2: ({node, children, ...props}) => (
                            <h2 className="text-xl font-bold mt-3 mb-2" {...props}>
                              {children}
                            </h2>
                          ),
                          h3: ({node, children, ...props}) => (
                            <h3 className="text-lg font-bold mt-2 mb-1" {...props}>
                              {children}
                            </h3>
                          ),
                          p: ({node, children, ...props}) => (
                            <p className="mb-2" {...props}>
                              {children}
                            </p>
                          ),
                        }}
                      >
                        {message.content}
                      </ReactMarkdown>
                    </div>
                  ) : (
                    <div className="whitespace-pre-wrap">{message.content}</div>
                  )}
                  <div
                    className={`text-xs mt-1 ${
                      message.role === 'user' ? 'text-indigo-200' : 'text-gray-500'
                    }`}
                  >
                    {message.timestamp?.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-white border border-gray-200 rounded-lg p-4">
                  <div className="flex space-x-2">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-75"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-150"></div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* File Upload Section */}
        <div className="border-t border-gray-200 p-4 bg-white">
          <div className="max-w-4xl mx-auto">
            <div className="flex items-center space-x-2 mb-2">
              <label className="flex items-center px-3 py-1.5 text-sm bg-gray-100 hover:bg-gray-200 rounded cursor-pointer transition">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                Choose File
                <input
                  type="file"
                  className="hidden"
                  onChange={handleFileChange}
                  disabled={uploadStatus?.loading}
                />
              </label>
              
              {selectedFile && (
                <span className="text-sm text-gray-600 truncate max-w-xs">
                  {selectedFile.name}
                </span>
              )}
              
              {selectedFile && (
                <button
                  onClick={handleFileUpload}
                  disabled={uploadStatus?.loading}
                  className="px-3 py-1.5 text-sm bg-indigo-600 text-white rounded hover:bg-indigo-700 transition disabled:opacity-50"
                >
                  {uploadStatus?.loading ? 'Uploading...' : 'Upload'}
                </button>
              )}
              
              {uploadStatus && (
                <span className={`text-sm ${uploadStatus.loading ? 'text-blue-600' : 'text-green-600'}`}>
                  {uploadStatus.message}
                </span>
              )}
            </div>
            
            <p className="text-xs text-gray-500 mb-3">
              Supported formats: DOCX, XLSX, and other document types
            </p>
          </div>
        </div>

        {/* Input Area */}
        <div className="border-t border-gray-200 p-4 bg-white">
          <div className="max-w-4xl mx-auto">
            <div className="flex">
              <textarea
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyPress}
                placeholder="Type your message here..."
                disabled={loading}
                className="flex-1 border border-gray-300 rounded-l-lg p-3 resize-none focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500"
                rows={3}
              />
              <button
                onClick={handleSend}
                disabled={!inputValue.trim() || loading}
                className="bg-indigo-600 text-white px-6 rounded-r-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
              >
                Send
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Chat