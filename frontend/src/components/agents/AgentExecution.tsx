import React, { useState, useCallback, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Play, 
  Square, 
  Loader2, 
  CheckCircle, 
  AlertCircle, 
  Clock,
  Brain,
  BarChart3,
  Search,
  Workflow
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { useToast } from '@/components/ui/notification'
import { 
  useExecuteAgent, 
  useAgentExecutionStatus, 
  useCreateSession,
  AgentExecutionRequest 
} from '@/hooks/api'
import { useAgentStatusWebSocket } from '@/hooks/useWebSocket'

export interface AgentExecutionComponentProps {
  sessionId?: string
  onExecutionComplete?: (result: any) => void
  onExecutionError?: (error: any) => void
  className?: string
}

const AGENT_TYPES = [
  {
    id: 'conversation',
    name: 'Conversation Agent',
    description: 'General-purpose conversational AI',
    icon: Brain,
    color: 'bg-blue-500',
  },
  {
    id: 'data_analysis',
    name: 'Data Analysis Agent',
    description: 'Specialized in data analysis and insights',
    icon: BarChart3,
    color: 'bg-green-500',
  },
  {
    id: 'research',
    name: 'Research Agent',
    description: 'Conducts research and information gathering',
    icon: Search,
    color: 'bg-purple-500',
  },
  {
    id: 'workflow',
    name: 'Workflow Agent',
    description: 'Orchestrates complex multi-step workflows',
    icon: Workflow,
    color: 'bg-orange-500',
  },
]

export function AgentExecutionComponent({
  sessionId: providedSessionId,
  onExecutionComplete,
  onExecutionError,
  className,
}: AgentExecutionComponentProps) {
  const [selectedAgentType, setSelectedAgentType] = useState('conversation')
  const [query, setQuery] = useState('')
  const [currentExecutionId, setCurrentExecutionId] = useState<string | null>(null)
  const [sessionId, setSessionId] = useState(providedSessionId)
  
  const { success, error, loading } = useToast()
  
  // Mutations and queries
  const executeAgent = useExecuteAgent()
  const createSession = useCreateSession()
  const executionStatus = useAgentExecutionStatus(
    currentExecutionId || '', 
    !!currentExecutionId
  )
  
  // WebSocket for real-time updates
  const {
    agentStatuses,
    executionUpdates,
    isConnected: wsConnected,
    status: wsStatus
  } = useAgentStatusWebSocket(sessionId || '', !!sessionId)

  // Create session if not provided
  useEffect(() => {
    if (!providedSessionId && !sessionId) {
      createSession.mutate({
        session_name: `Agent Session ${new Date().toLocaleTimeString()}`,
        metadata: { created_from: 'agent_execution_component' }
      }, {
        onSuccess: (data) => {
          setSessionId(data.session_id)
        },
        onError: (err) => {
          error('Failed to create session', {
            message: 'Please try again or refresh the page'
          })
        }
      })
    }
  }, [providedSessionId, sessionId, createSession, error])

  const handleExecuteAgent = useCallback(async () => {
    if (!query.trim()) {
      error('Please enter a query')
      return
    }

    if (!sessionId) {
      error('Session not ready. Please wait...')
      return
    }

    const request: AgentExecutionRequest = {
      agent_type: selectedAgentType,
      query: query.trim(),
      session_id: sessionId,
      parameters: {
        timestamp: new Date().toISOString(),
        source: 'agent_execution_component'
      }
    }

    const loadingId = loading(`Executing ${AGENT_TYPES.find(a => a.id === selectedAgentType)?.name}...`)

    executeAgent.mutate(request, {
      onSuccess: (data) => {
        setCurrentExecutionId(data.execution_id)
        success('Agent execution started', {
          message: `Execution ID: ${data.execution_id.slice(0, 8)}...`,
          duration: 3000
        })
      },
      onError: (err) => {
        error('Failed to execute agent', {
          message: err.message || 'Please try again'
        })
        onExecutionError?.(err)
      }
    })
  }, [query, selectedAgentType, sessionId, executeAgent, success, error, loading, onExecutionError])

  const handleStopExecution = useCallback(() => {
    // In a real implementation, you'd call an API to stop the execution
    setCurrentExecutionId(null)
    success('Execution stopped')
  }, [success])

  // Handle execution completion
  useEffect(() => {
    if (executionStatus.data?.status === 'completed') {
      success('Agent execution completed!', {
        message: 'Check the results below',
        duration: 5000
      })
      onExecutionComplete?.(executionStatus.data.result)
      // Don't clear execution ID immediately - let user see the results
    } else if (executionStatus.data?.status === 'failed') {
      error('Agent execution failed', {
        message: executionStatus.data.error || 'Unknown error occurred',
        duration: 8000
      })
      onExecutionError?.(executionStatus.data.error)
    }
  }, [executionStatus.data, success, error, onExecutionComplete, onExecutionError])

  const isExecuting = currentExecutionId && 
    (executionStatus.data?.status === 'pending' || executionStatus.data?.status === 'running')

  const selectedAgent = AGENT_TYPES.find(a => a.id === selectedAgentType)
  const currentStatus = currentExecutionId ? agentStatuses[currentExecutionId] || executionStatus.data : null

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Brain className="w-5 h-5 text-blue-500" />
          AI Agent Execution
          {wsConnected && (
            <Badge variant="outline" className="ml-auto">
              <div className="w-2 h-2 bg-green-500 rounded-full mr-1 animate-pulse" />
              Live
            </Badge>
          )}
        </CardTitle>
      </CardHeader>
      
      <CardContent className="space-y-6">
        {/* Agent Type Selection */}
        <div>
          <label className="text-sm font-medium mb-3 block">Select Agent Type</label>
          <div className="grid grid-cols-2 gap-2">
            {AGENT_TYPES.map((agent) => {
              const Icon = agent.icon
              return (
                <button
                  key={agent.id}
                  onClick={() => setSelectedAgentType(agent.id)}
                  disabled={isExecuting}
                  className={`
                    p-3 rounded-lg border text-left transition-all duration-200
                    ${selectedAgentType === agent.id 
                      ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' 
                      : 'border-gray-200 hover:border-gray-300 dark:border-gray-700 dark:hover:border-gray-600'
                    }
                    ${isExecuting ? 'opacity-50 cursor-not-allowed' : 'hover:shadow-sm'}
                  `}
                >
                  <div className="flex items-center gap-2 mb-1">
                    <div className={`w-8 h-8 rounded ${agent.color} flex items-center justify-center`}>
                      <Icon className="w-4 h-4 text-white" />
                    </div>
                    <span className="font-medium text-sm">{agent.name}</span>
                  </div>
                  <p className="text-xs text-gray-600 dark:text-gray-400">
                    {agent.description}
                  </p>
                </button>
              )
            })}
          </div>
        </div>

        {/* Query Input */}
        <div>
          <label className="text-sm font-medium mb-2 block">Query or Task</label>
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            disabled={isExecuting}
            placeholder={`Ask the ${selectedAgent?.name} to help you with something...`}
            className="w-full p-3 border rounded-lg resize-none h-24 focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
          />
          <p className="text-xs text-gray-500 mt-1">
            Describe what you want the agent to do or analyze
          </p>
        </div>

        {/* Execution Controls */}
        <div className="flex gap-2">
          {!isExecuting ? (
            <Button
              onClick={handleExecuteAgent}
              disabled={!query.trim() || !sessionId || executeAgent.isPending}
              className="flex-1"
            >
              {executeAgent.isPending ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <Play className="w-4 h-4 mr-2" />
              )}
              Execute Agent
            </Button>
          ) : (
            <Button
              onClick={handleStopExecution}
              variant="destructive"
              className="flex-1"
            >
              <Square className="w-4 h-4 mr-2" />
              Stop Execution
            </Button>
          )}
        </div>

        {/* Execution Status */}
        <AnimatePresence>
          {currentStatus && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="border rounded-lg p-4 bg-gray-50 dark:bg-gray-900/50"
            >
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  {currentStatus.status === 'pending' && (
                    <Clock className="w-4 h-4 text-yellow-500" />
                  )}
                  {currentStatus.status === 'running' && (
                    <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />
                  )}
                  {currentStatus.status === 'completed' && (
                    <CheckCircle className="w-4 h-4 text-green-500" />
                  )}
                  {currentStatus.status === 'failed' && (
                    <AlertCircle className="w-4 h-4 text-red-500" />
                  )}
                  <span className="font-medium capitalize">
                    {currentStatus.status}
                  </span>
                </div>
                
                <Badge variant="outline">
                  {currentExecutionId?.slice(0, 8)}...
                </Badge>
              </div>

              {/* Progress Bar */}
              {currentStatus.progress !== undefined && (
                <div className="mb-3">
                  <div className="flex justify-between text-sm mb-1">
                    <span>Progress</span>
                    <span>{Math.round(currentStatus.progress)}%</span>
                  </div>
                  <Progress value={currentStatus.progress} className="h-2" />
                </div>
              )}

              {/* Status Message */}
              {currentStatus.message && (
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                  {currentStatus.message}
                </p>
              )}

              {/* Results */}
              {currentStatus.result && (
                <div className="mt-3 p-3 bg-white dark:bg-gray-800 rounded border">
                  <h4 className="font-medium mb-2">Results:</h4>
                  <pre className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
                    {typeof currentStatus.result === 'string' 
                      ? currentStatus.result 
                      : JSON.stringify(currentStatus.result, null, 2)
                    }
                  </pre>
                </div>
              )}

              {/* Error */}
              {currentStatus.error && (
                <div className="mt-3 p-3 bg-red-50 dark:bg-red-900/20 rounded border border-red-200 dark:border-red-800">
                  <h4 className="font-medium text-red-700 dark:text-red-300 mb-2">Error:</h4>
                  <p className="text-sm text-red-600 dark:text-red-400">
                    {currentStatus.error}
                  </p>
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Recent Execution Updates */}
        {executionUpdates.length > 0 && (
          <div>
            <h4 className="font-medium text-sm mb-2">Recent Updates</h4>
            <div className="space-y-2 max-h-32 overflow-y-auto">
              {executionUpdates.slice(0, 5).map((update, index) => (
                <div 
                  key={index}
                  className="text-xs p-2 bg-gray-100 dark:bg-gray-800 rounded border"
                >
                  <div className="flex justify-between items-center">
                    <span className="font-medium">{update.type}</span>
                    <span className="text-gray-500">
                      {new Date(update.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  {update.message && (
                    <p className="mt-1 text-gray-600 dark:text-gray-400">
                      {update.message}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Connection Status */}
        {!wsConnected && sessionId && (
          <div className="text-xs text-amber-600 dark:text-amber-400 flex items-center gap-1">
            <AlertCircle className="w-3 h-3" />
            Real-time updates unavailable. Using polling fallback.
          </div>
        )}
      </CardContent>
    </Card>
  )
}
