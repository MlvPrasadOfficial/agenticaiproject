import { useState, useEffect, useCallback, useRef } from 'react'
import { useWebSocket } from './useWebSocket'
import { useNotification } from '@/components/ui/notification'

export interface AgentStatus {
  executionId: string
  agentType: string
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
  progress: number
  currentStep?: string
  steps: Array<{
    name: string
    status: 'pending' | 'running' | 'completed' | 'failed'
    startTime?: string
    endTime?: string
    result?: any
    error?: string
  }>
  startTime: string
  endTime?: string
  result?: any
  error?: string
}

export interface DataProcessingStatus {
  fileId: string
  filename: string
  status: 'uploading' | 'processing' | 'completed' | 'failed'
  progress: number
  stage?: string
  preview?: any
  analysis?: any
  error?: string
}

export interface ConversationStatus {
  sessionId: string
  messageId?: string
  status: 'typing' | 'processing' | 'completed' | 'failed'
  agentExecutions?: string[]
}

export interface SystemHealth {
  status: 'healthy' | 'degraded' | 'unhealthy'
  services: {
    api: boolean
    database: boolean
    agents: boolean
    rag: boolean
    websocket: boolean
  }
  lastCheck: string
  metrics?: {
    responseTime: number
    memoryUsage: number
    cpuUsage: number
    activeConnections: number
  }
}

export interface RealTimeState {
  agentExecutions: Map<string, AgentStatus>
  dataProcessing: Map<string, DataProcessingStatus>
  conversations: Map<string, ConversationStatus>
  systemHealth: SystemHealth
  notifications: any[]
}

interface UseRealTimeStatusOptions {
  sessionId?: string
  enablePolling?: boolean
  pollingInterval?: number
  enableWebSocket?: boolean
  onAgentUpdate?: (status: AgentStatus) => void
  onDataUpdate?: (status: DataProcessingStatus) => void
  onConversationUpdate?: (status: ConversationStatus) => void
  onSystemHealthUpdate?: (health: SystemHealth) => void
}

export function useRealTimeStatus({
  sessionId,
  enablePolling = true,
  pollingInterval = 2000,
  enableWebSocket = true,
  onAgentUpdate,
  onDataUpdate,
  onConversationUpdate,
  onSystemHealthUpdate,
}: UseRealTimeStatusOptions = {}) {
  const [state, setState] = useState<RealTimeState>({
    agentExecutions: new Map(),
    dataProcessing: new Map(),
    conversations: new Map(),
    systemHealth: {
      status: 'healthy',
      services: {
        api: true,
        database: true,
        agents: true,
        rag: true,
        websocket: false,
      },
      lastCheck: new Date().toISOString(),
    },
    notifications: [],
  })

  const pollingRef = useRef<NodeJS.Timeout | null>(null)
  const { addNotification } = useNotification()

  // WebSocket connection for real-time updates
  const wsUrl = `ws://localhost:8000/ws${sessionId ? `?session_id=${sessionId}` : ''}`
  
  const handleWebSocketMessage = useCallback((message: any) => {
    try {
      const data = typeof message === 'string' ? JSON.parse(message) : message
      
      switch (data.type) {
        case 'agent_status':
          setState(prev => {
            const newExecutions = new Map(prev.agentExecutions)
            newExecutions.set(data.payload.executionId, data.payload)
            onAgentUpdate?.(data.payload)
            return { ...prev, agentExecutions: newExecutions }
          })
          break
          
        case 'data_processing':
          setState(prev => {
            const newProcessing = new Map(prev.dataProcessing)
            newProcessing.set(data.payload.fileId, data.payload)
            onDataUpdate?.(data.payload)
            return { ...prev, dataProcessing: newProcessing }
          })
          break
          
        case 'conversation_update':
          setState(prev => {
            const newConversations = new Map(prev.conversations)
            newConversations.set(data.payload.sessionId, data.payload)
            onConversationUpdate?.(data.payload)
            return { ...prev, conversations: newConversations }
          })
          break
          
        case 'system_health':
          setState(prev => {
            onSystemHealthUpdate?.(data.payload)
            return { ...prev, systemHealth: data.payload }
          })
          break
          
        case 'notification':
          addNotification(data.payload)
          setState(prev => ({
            ...prev,
            notifications: [...prev.notifications, data.payload]
          }))
          break
      }
    } catch (error) {
      console.error('Failed to parse WebSocket message:', error)
    }
  }, [onAgentUpdate, onDataUpdate, onConversationUpdate, onSystemHealthUpdate, addNotification])

  const { status: wsStatus, sendMessage } = useWebSocket({
    url: wsUrl,
    sessionId,
    onMessage: handleWebSocketMessage,
    enabled: enableWebSocket,
  })

  // Polling fallback for when WebSocket is not available
  const pollStatus = useCallback(async () => {
    try {
      // Poll agent executions
      const agentResponse = await fetch('/api/v1/agents/status', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          ...(sessionId && { 'X-Session-ID': sessionId }),
        },
      })
      
      if (agentResponse.ok) {
        const agentData = await agentResponse.json()
        if (agentData.executions) {
          setState(prev => {
            const newExecutions = new Map(prev.agentExecutions)
            agentData.executions.forEach((execution: AgentStatus) => {
              newExecutions.set(execution.executionId, execution)
            })
            return { ...prev, agentExecutions: newExecutions }
          })
        }
      }

      // Poll system health
      const healthResponse = await fetch('/api/v1/health/detailed', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      })
      
      if (healthResponse.ok) {
        const healthData = await healthResponse.json()
        setState(prev => {
          onSystemHealthUpdate?.(healthData)
          return { ...prev, systemHealth: healthData }
        })
      }
    } catch (error) {
      console.error('Polling error:', error)
    }
  }, [sessionId, onSystemHealthUpdate])

  // Set up polling
  useEffect(() => {
    if (enablePolling && (!enableWebSocket || !wsStatus.connected)) {
      pollingRef.current = setInterval(pollStatus, pollingInterval)
      
      // Initial poll
      pollStatus()
      
      return () => {
        if (pollingRef.current) {
          clearInterval(pollingRef.current)
        }
      }
    }
  }, [enablePolling, enableWebSocket, wsStatus.connected, pollStatus, pollingInterval])

  // Cleanup polling when WebSocket connects
  useEffect(() => {
    if (wsStatus.connected && pollingRef.current) {
      clearInterval(pollingRef.current)
      pollingRef.current = null
    }
  }, [wsStatus.connected])

  // Update WebSocket service status
  useEffect(() => {
    setState(prev => ({
      ...prev,
      systemHealth: {
        ...prev.systemHealth,
        services: {
          ...prev.systemHealth.services,
          websocket: wsStatus.connected,
        },
        lastCheck: new Date().toISOString(),
      }
    }))
  }, [wsStatus.connected])

  const startAgentExecution = useCallback((agentType: string, config: any) => {
    const executionId = Math.random().toString(36).substring(7)
    
    // Add initial status
    setState(prev => {
      const newExecutions = new Map(prev.agentExecutions)
      newExecutions.set(executionId, {
        executionId,
        agentType,
        status: 'pending',
        progress: 0,
        steps: [],
        startTime: new Date().toISOString(),
      })
      return { ...prev, agentExecutions: newExecutions }
    })

    return executionId
  }, [])

  const startDataProcessing = useCallback((file: File) => {
    const fileId = Math.random().toString(36).substring(7)
    
    // Add initial status
    setState(prev => {
      const newProcessing = new Map(prev.dataProcessing)
      newProcessing.set(fileId, {
        fileId,
        filename: file.name,
        status: 'uploading',
        progress: 0,
      })
      return { ...prev, dataProcessing: newProcessing }
    })

    return fileId
  }, [])

  const getAgentStatus = useCallback((executionId: string) => {
    return state.agentExecutions.get(executionId)
  }, [state.agentExecutions])

  const getDataProcessingStatus = useCallback((fileId: string) => {
    return state.dataProcessing.get(fileId)
  }, [state.dataProcessing])

  const getConversationStatus = useCallback((sessionId: string) => {
    return state.conversations.get(sessionId)
  }, [state.conversations])

  const clearCompletedExecutions = useCallback(() => {
    setState(prev => {
      const newExecutions = new Map()
      prev.agentExecutions.forEach((execution, id) => {
        if (!['completed', 'failed', 'cancelled'].includes(execution.status)) {
          newExecutions.set(id, execution)
        }
      })
      return { ...prev, agentExecutions: newExecutions }
    })
  }, [])

  const clearCompletedProcessing = useCallback(() => {
    setState(prev => {
      const newProcessing = new Map()
      prev.dataProcessing.forEach((processing, id) => {
        if (!['completed', 'failed'].includes(processing.status)) {
          newProcessing.set(id, processing)
        }
      })
      return { ...prev, dataProcessing: newProcessing }
    })
  }, [])

  return {
    ...state,
    wsStatus,
    isConnected: wsStatus.connected,
    startAgentExecution,
    startDataProcessing,
    getAgentStatus,
    getDataProcessingStatus,
    getConversationStatus,
    clearCompletedExecutions,
    clearCompletedProcessing,
    sendMessage,
  }
}
