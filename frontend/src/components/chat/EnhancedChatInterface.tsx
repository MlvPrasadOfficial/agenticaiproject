import React, { useState, useRef, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Send, 
  Loader2, 
  User, 
  Bot, 
  MessageSquare,
  Trash2,
  RefreshCw,
  Copy,
  ThumbsUp,
  ThumbsDown
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Textarea } from '@/components/ui/textarea'
import { ScrollArea } from '@/components/ui/scroll-area'
import { useToast } from '@/components/ui/notification'
import { 
  useSendMessage,
  useConversationHistory,
  useCreateSession,
  ConversationMessage,
  ConversationRequest
} from '@/hooks/api'
import { useAgentStatusWebSocket } from '@/hooks/useWebSocket'

export interface EnhancedChatInterfaceProps {
  sessionId?: string
  onNewSession?: (sessionId: string) => void
  onMessageSent?: (message: ConversationMessage) => void
  className?: string
  height?: string
}

export function EnhancedChatInterface({
  sessionId: providedSessionId,
  onNewSession,
  onMessageSent,
  className,
  height = '600px'
}: EnhancedChatInterfaceProps) {
  const [message, setMessage] = useState('')
  const [sessionId, setSessionId] = useState(providedSessionId)
  const [isTyping, setIsTyping] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  
  const { success, error } = useToast()
  
  // API hooks
  const sendMessage = useSendMessage()
  const createSession = useCreateSession()
  const conversationHistory = useConversationHistory(sessionId || '', !!sessionId)
  
  // WebSocket for real-time updates
  const { isConnected: wsConnected } = useAgentStatusWebSocket(sessionId || '', !!sessionId)

  // Create session if not provided
  useEffect(() => {
    if (!providedSessionId && !sessionId) {
      createSession.mutate({
        session_name: `Chat Session ${new Date().toLocaleTimeString()}`,
        metadata: { created_from: 'chat_interface' }
      }, {
        onSuccess: (data) => {
          setSessionId(data.session_id)
          onNewSession?.(data.session_id)
          success('New chat session started')
        },
        onError: (err) => {
          error('Failed to create chat session', {
            message: 'Please try again or refresh the page'
          })
        }
      })
    }
  }, [providedSessionId, sessionId, createSession, onNewSession, success, error])

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [conversationHistory.data])

  // Handle message sending
  const handleSendMessage = useCallback(async () => {
    if (!message.trim() || !sessionId || sendMessage.isPending) {
      return
    }

    const messageText = message.trim()
    setMessage('')
    setIsTyping(true)

    const request: ConversationRequest = {
      session_id: sessionId,
      message: messageText,
      context: {
        timestamp: new Date().toISOString(),
        source: 'chat_interface'
      }
    }

    sendMessage.mutate(request, {
      onSuccess: (data) => {
        setIsTyping(false)
        onMessageSent?.(data)
        // Conversation history will be updated automatically via React Query
      },
      onError: (err) => {
        setIsTyping(false)
        error('Failed to send message', {
          message: err.message || 'Please try again'
        })
      }
    })
  }, [message, sessionId, sendMessage, onMessageSent, error])

  // Handle Enter key press
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  // Handle message actions
  const handleCopyMessage = useCallback((text: string) => {
    navigator.clipboard.writeText(text)
    success('Message copied to clipboard')
  }, [success])

  const handleClearChat = useCallback(() => {
    // In a real implementation, you'd call an API to clear the conversation
    conversationHistory.refetch()
    success('Chat cleared')
  }, [conversationHistory, success])

  const handleNewSession = useCallback(() => {
    setSessionId(undefined)
    // This will trigger the useEffect to create a new session
  }, [])

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current
    if (textarea) {
      textarea.style.height = 'auto'
      textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`
    }
  }, [message])

  const messages = conversationHistory.data || []

  return (
    <Card className={className} style={{ height }}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <MessageSquare className="w-5 h-5 text-blue-500" />
            AI Chat Assistant
            {wsConnected && (
              <Badge variant="outline" className="ml-2">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-1 animate-pulse" />
                Live
              </Badge>
            )}
          </CardTitle>
          
          <div className="flex gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => conversationHistory.refetch()}
              disabled={conversationHistory.isLoading}
            >
              <RefreshCw className="w-4 h-4" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleClearChat}
            >
              <Trash2 className="w-4 h-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={handleNewSession}
            >
              New Chat
            </Button>
          </div>
        </div>
        
        {sessionId && (
          <p className="text-xs text-gray-500">
            Session: {sessionId.slice(0, 8)}...
          </p>
        )}
      </CardHeader>
      
      <CardContent className="flex flex-col h-full p-0">
        {/* Messages Area */}
        <ScrollArea className="flex-1 p-4">
          <div className="space-y-4">
            {conversationHistory.isLoading && (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="w-6 h-6 animate-spin text-gray-400" />
                <span className="ml-2 text-gray-500">Loading conversation...</span>
              </div>
            )}
            
            {messages.length === 0 && !conversationHistory.isLoading && (
              <div className="text-center py-8 text-gray-500">
                <Bot className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                <p className="text-lg font-medium mb-2">Welcome to AI Chat!</p>
                <p className="text-sm">
                  Start a conversation with our AI assistant. Ask questions, request analysis, or get help with your data.
                </p>
              </div>
            )}
            
            {messages.map((msg, index) => (
              <AnimatePresence key={`${msg.id}-${index}`}>
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.3, delay: index * 0.1 }}
                >
                  {/* User Message */}
                  <div className="flex justify-end mb-4">
                    <div className="flex items-start gap-2 max-w-[80%]">
                      <div className="bg-blue-500 text-white p-3 rounded-lg rounded-tr-none">
                        <p className="whitespace-pre-wrap">{msg.message}</p>
                        <div className="flex items-center justify-between mt-2 text-xs opacity-70">
                          <span>{new Date(msg.timestamp).toLocaleTimeString()}</span>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleCopyMessage(msg.message)}
                            className="h-auto p-1 text-white hover:bg-blue-600"
                          >
                            <Copy className="w-3 h-3" />
                          </Button>
                        </div>
                      </div>
                      <div className="w-8 h-8 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                        <User className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                      </div>
                    </div>
                  </div>
                  
                  {/* AI Response */}
                  <div className="flex justify-start mb-4">
                    <div className="flex items-start gap-2 max-w-[80%]">
                      <div className="w-8 h-8 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                        <Bot className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                      </div>
                      <div className="bg-gray-100 dark:bg-gray-800 p-3 rounded-lg rounded-tl-none">
                        <p className="whitespace-pre-wrap">{msg.response}</p>
                        <div className="flex items-center justify-between mt-2 text-xs text-gray-500">
                          <span>{new Date(msg.timestamp).toLocaleTimeString()}</span>
                          <div className="flex gap-1">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleCopyMessage(msg.response)}
                              className="h-auto p-1 hover:bg-gray-200 dark:hover:bg-gray-700"
                            >
                              <Copy className="w-3 h-3" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              className="h-auto p-1 hover:bg-gray-200 dark:hover:bg-gray-700"
                            >
                              <ThumbsUp className="w-3 h-3" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              className="h-auto p-1 hover:bg-gray-200 dark:hover:bg-gray-700"
                            >
                              <ThumbsDown className="w-3 h-3" />
                            </Button>
                          </div>
                        </div>
                        
                        {/* Show agent type if available */}
                        {msg.agent_type && (
                          <Badge variant="outline" className="mt-2 text-xs">
                            {msg.agent_type.replace('_', ' ')}
                          </Badge>
                        )}
                      </div>
                    </div>
                  </div>
                </motion.div>
              </AnimatePresence>
            ))}
            
            {/* Typing Indicator */}
            {isTyping && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex justify-start"
              >
                <div className="flex items-start gap-2">
                  <div className="w-8 h-8 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center flex-shrink-0">
                    <Bot className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                  </div>
                  <div className="bg-gray-100 dark:bg-gray-800 p-3 rounded-lg rounded-tl-none">
                    <div className="flex gap-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
        </ScrollArea>
        
        {/* Input Area */}
        <div className="border-t p-4">
          <div className="flex gap-2">
            <div className="flex-1">
              <Textarea
                ref={textareaRef}
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask me anything..."
                disabled={!sessionId || sendMessage.isPending}
                className="min-h-[44px] max-h-[120px] resize-none"
                rows={1}
              />
            </div>
            <Button
              onClick={handleSendMessage}
              disabled={!message.trim() || !sessionId || sendMessage.isPending}
              size="lg"
            >
              {sendMessage.isPending ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
            </Button>
          </div>
          
          {!wsConnected && sessionId && (
            <p className="text-xs text-amber-600 dark:text-amber-400 mt-2">
              Real-time features unavailable. Messages will still be delivered.
            </p>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
