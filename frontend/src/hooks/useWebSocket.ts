import { useEffect, useRef, useState, useCallback } from 'react'
import { useNotification } from '@/components/ui/notification'

export interface WebSocketMessage {
  type: string
  payload: any
  timestamp: string
}

export interface WebSocketStatus {
  connected: boolean
  connecting: boolean
  error: string | null
  reconnectAttempts: number
}

export interface UseWebSocketOptions {
  url: string
  sessionId?: string
  reconnectInterval?: number
  maxReconnectAttempts?: number
  onMessage?: (message: WebSocketMessage) => void
  onStatusChange?: (status: WebSocketStatus) => void
  onError?: (error: Event) => void
  enabled?: boolean
}

export function useWebSocket({
  url,
  sessionId,
  reconnectInterval = 3000,
  maxReconnectAttempts = 5,
  onMessage,
  onStatusChange,
  onError,
  enabled = true,
}: UseWebSocketOptions) {
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const reconnectAttemptsRef = useRef(0)
  const { addNotification } = useNotification()

  const [status, setStatus] = useState<WebSocketStatus>({
    connected: false,
    connecting: false,
    error: null,
    reconnectAttempts: 0,
  })

  const updateStatus = useCallback((updates: Partial<WebSocketStatus>) => {
    setStatus(prev => {
      const newStatus = { ...prev, ...updates }
      onStatusChange?.(newStatus)
      return newStatus
    })
  }, [onStatusChange])

  const connect = useCallback(() => {
    if (!enabled || !url) return

    // Don't connect if already connected or connecting
    if (wsRef.current?.readyState === WebSocket.OPEN || 
        wsRef.current?.readyState === WebSocket.CONNECTING) {
      return
    }

    updateStatus({ connecting: true, error: null })

    try {
      // Build WebSocket URL with session ID if provided
      const wsUrl = sessionId ? `${url}/${sessionId}` : url
      const ws = new WebSocket(wsUrl)

      ws.onopen = () => {
        console.log('WebSocket connected:', wsUrl)
        reconnectAttemptsRef.current = 0
        updateStatus({
          connected: true,
          connecting: false,
          error: null,
          reconnectAttempts: 0,
        })
        
        addNotification({
          title: 'Connected',
          description: 'Real-time updates enabled',
          type: 'success',
        })
      }

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          onMessage?.(message)
          
          // Handle specific message types
          if (message.type === 'agent_status') {
            addNotification({
              title: 'Agent Update',
              description: message.payload.message || 'Agent status updated',
              type: 'info',
            })
          } else if (message.type === 'error') {
            addNotification({
              title: 'Error',
              description: message.payload.message || 'An error occurred',
              type: 'error',
            })
          }
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }

      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        onError?.(error)
        updateStatus({ error: 'Connection error' })
      }

      ws.onclose = (event) => {
        console.log('WebSocket closed:', event.code, event.reason)
        updateStatus({ connected: false, connecting: false })

        // Attempt reconnection if not manually closed and under max attempts
        if (event.code !== 1000 && reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current += 1
          updateStatus({ 
            reconnectAttempts: reconnectAttemptsRef.current,
            error: `Reconnecting... (${reconnectAttemptsRef.current}/${maxReconnectAttempts})`
          })

          reconnectTimeoutRef.current = setTimeout(() => {
            connect()
          }, reconnectInterval)
        } else if (reconnectAttemptsRef.current >= maxReconnectAttempts) {
          updateStatus({ 
            error: 'Maximum reconnection attempts reached',
            reconnectAttempts: reconnectAttemptsRef.current 
          })
          addNotification({
            title: 'Connection Failed',
            description: 'Unable to establish real-time connection. Using polling fallback.',
            type: 'warning',
          })
        }
      }

      wsRef.current = ws
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error)
      updateStatus({ 
        connecting: false, 
        error: 'Failed to create connection' 
      })
    }
  }, [url, sessionId, enabled, maxReconnectAttempts, reconnectInterval, onMessage, onError, updateStatus, addNotification])

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }

    if (wsRef.current) {
      wsRef.current.close(1000, 'Manual disconnect')
      wsRef.current = null
    }

    updateStatus({
      connected: false,
      connecting: false,
      error: null,
      reconnectAttempts: 0,
    })
  }, [updateStatus])

  const sendMessage = useCallback((message: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      const wsMessage: WebSocketMessage = {
        type: typeof message === 'string' ? 'message' : message.type || 'message',
        payload: typeof message === 'string' ? { text: message } : message,
        timestamp: new Date().toISOString(),
      }
      wsRef.current.send(JSON.stringify(wsMessage))
      return true
    }
    return false
  }, [])

  const reconnect = useCallback(() => {
    disconnect()
    reconnectAttemptsRef.current = 0
    connect()
  }, [disconnect, connect])

  // Connect on mount if enabled
  useEffect(() => {
    if (enabled) {
      connect()
    }

    return () => {
      disconnect()
    }
  }, [enabled, connect, disconnect])

  return {
    status,
    sendMessage,
    reconnect,
    disconnect,
    isConnected: status.connected,
    isConnecting: status.connecting,
    error: status.error,
  }
}

// Specialized hook for agent status updates
export function useAgentStatusWebSocket(sessionId: string, enabled: boolean = true) {
  const [agentStatuses, setAgentStatuses] = useState<Record<string, any>>({})
  const [executionUpdates, setExecutionUpdates] = useState<any[]>([])

  const handleMessage = useCallback((message: WebSocketMessage) => {
    switch (message.type) {
      case 'agent_status':
        setAgentStatuses(prev => ({
          ...prev,
          [message.payload.execution_id]: message.payload,
        }))
        break
      case 'execution_update':
        setExecutionUpdates(prev => [message.payload, ...prev.slice(0, 99)]) // Keep last 100
        break
      case 'workflow_status':
        // Handle workflow status updates
        break
    }
  }, [])

  const ws = useWebSocket({
    url: `ws://localhost:8000/ws/status`,
    sessionId,
    onMessage: handleMessage,
    enabled,
  })

  return {
    ...ws,
    agentStatuses,
    executionUpdates,
    clearUpdates: () => setExecutionUpdates([]),
  }
}

// Hook for data processing status updates
export function useDataProcessingWebSocket(fileId?: string, enabled: boolean = true) {
  const [processingStatus, setProcessingStatus] = useState<any>(null)
  const [analysisResults, setAnalysisResults] = useState<any>(null)

  const handleMessage = useCallback((message: WebSocketMessage) => {
    switch (message.type) {
      case 'data_processing':
        if (!fileId || message.payload.file_id === fileId) {
          setProcessingStatus(message.payload)
        }
        break
      case 'analysis_complete':
        if (!fileId || message.payload.file_id === fileId) {
          setAnalysisResults(message.payload)
        }
        break
    }
  }, [fileId])

  const ws = useWebSocket({
    url: `ws://localhost:8000/ws/data`,
    sessionId: fileId,
    onMessage: handleMessage,
    enabled: enabled && !!fileId,
  })

  return {
    ...ws,
    processingStatus,
    analysisResults,
  }
}
