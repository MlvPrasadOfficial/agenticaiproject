import React from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Activity, 
  CheckCircle, 
  AlertCircle, 
  Clock, 
  Zap,
  Database,
  Wifi,
  WifiOff,
  TrendingUp,
  Users,
  HardDrive
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { useRealTimeStatus } from '@/hooks/useRealTimeStatus'

interface RealTimeStatusDashboardProps {
  readonly sessionId?: string
  readonly compact?: boolean
}

export function RealTimeStatusDashboard({ sessionId, compact = false }: RealTimeStatusDashboardProps) {
  const {
    agentExecutions,
    dataProcessing,
    systemHealth,
    isConnected,
    clearCompletedExecutions,
    clearCompletedProcessing,
  } = useRealTimeStatus({ sessionId })

  const activeExecutions = Array.from(agentExecutions.values()).filter(
    ex => !['completed', 'failed', 'cancelled'].includes(ex.status)
  )
  
  const activeProcessing = Array.from(dataProcessing.values()).filter(
    proc => !['completed', 'failed'].includes(proc.status)
  )

  const completedExecutions = Array.from(agentExecutions.values()).filter(
    ex => ['completed', 'failed', 'cancelled'].includes(ex.status)
  )

  if (compact) {
    return (
      <div className="flex items-center gap-2">
        {/* Connection Status */}
        <Badge variant={isConnected ? 'success' : 'destructive'} className="gap-1">
          {isConnected ? <Wifi className="w-3 h-3" /> : <WifiOff className="w-3 h-3" />}
          {isConnected ? 'Live' : 'Offline'}
        </Badge>

        {/* Active Executions */}
        {activeExecutions.length > 0 && (
          <Badge variant="outline" className="gap-1">
            <Activity className="w-3 h-3" />
            {activeExecutions.length} running
          </Badge>
        )}

        {/* System Health */}
        <Badge 
          variant={
            systemHealth.status === 'healthy' ? 'success' :
            systemHealth.status === 'degraded' ? 'warning' : 'destructive'
          }
          className="gap-1"
        >
          <Activity className="w-3 h-3" />
          {systemHealth.status}
        </Badge>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* System Health Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="w-5 h-5" />
            System Health
            <Badge 
              variant={
                systemHealth.status === 'healthy' ? 'success' :
                systemHealth.status === 'degraded' ? 'warning' : 'destructive'
              }
            >
              {systemHealth.status}
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
            {Object.entries(systemHealth.services).map(([service, status]) => (
              <div key={service} className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${status ? 'bg-green-500' : 'bg-red-500'}`} />
                <span className="text-sm capitalize">{service}</span>
                {status ? (
                  <CheckCircle className="w-4 h-4 text-green-500" />
                ) : (
                  <AlertCircle className="w-4 h-4 text-red-500" />
                )}
              </div>
            ))}
          </div>

          {systemHealth.metrics && (
            <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div className="flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-blue-500" />
                Response: {systemHealth.metrics.responseTime}ms
              </div>
              <div className="flex items-center gap-2">
                <HardDrive className="w-4 h-4 text-purple-500" />
                Memory: {systemHealth.metrics.memoryUsage}%
              </div>
              <div className="flex items-center gap-2">
                <Zap className="w-4 h-4 text-yellow-500" />
                CPU: {systemHealth.metrics.cpuUsage}%
              </div>
              <div className="flex items-center gap-2">
                <Users className="w-4 h-4 text-green-500" />
                Connections: {systemHealth.metrics.activeConnections}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Connection Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            {isConnected ? <Wifi className="w-5 h-5 text-green-500" /> : <WifiOff className="w-5 h-5 text-red-500" />}
            Real-time Connection
            <Badge variant={isConnected ? 'success' : 'destructive'}>
              {isConnected ? 'Connected' : 'Disconnected'}
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            {isConnected 
              ? 'Receiving real-time updates via WebSocket connection'
              : 'Using polling fallback for status updates'
            }
          </p>
        </CardContent>
      </Card>

      {/* Active Agent Executions */}
      {activeExecutions.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Activity className="w-5 h-5 text-blue-500" />
                Active Agent Executions
                <Badge variant="outline">{activeExecutions.length}</Badge>
              </div>
              {completedExecutions.length > 0 && (
                <Button variant="outline" size="sm" onClick={clearCompletedExecutions}>
                  Clear Completed
                </Button>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <AnimatePresence>
                {activeExecutions.map((execution) => (
                  <motion.div
                    key={execution.executionId}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    className="border rounded-lg p-4 space-y-2"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Badge variant="outline">{execution.agentType}</Badge>
                        <span className="text-sm font-medium">
                          {execution.executionId.slice(0, 8)}...
                        </span>
                      </div>
                      <Badge 
                        variant={
                          execution.status === 'running' ? 'default' :
                          execution.status === 'completed' ? 'success' :
                          execution.status === 'failed' ? 'destructive' : 'secondary'
                        }
                      >
                        {execution.status}
                      </Badge>
                    </div>

                    {execution.currentStep && (
                      <p className="text-sm text-muted-foreground">
                        Current: {execution.currentStep}
                      </p>
                    )}

                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <motion.div
                        className="bg-blue-500 h-2 rounded-full"
                        initial={{ width: 0 }}
                        animate={{ width: `${execution.progress}%` }}
                        transition={{ duration: 0.5 }}
                      />
                    </div>

                    <div className="flex items-center gap-4 text-xs text-muted-foreground">
                      <span>Started: {new Date(execution.startTime).toLocaleTimeString()}</span>
                      {execution.steps.length > 0 && (
                        <span>Steps: {execution.steps.filter(s => s.status === 'completed').length}/{execution.steps.length}</span>
                      )}
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Active Data Processing */}
      {activeProcessing.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Database className="w-5 h-5 text-purple-500" />
                Data Processing
                <Badge variant="outline">{activeProcessing.length}</Badge>
              </div>
              <Button variant="outline" size="sm" onClick={clearCompletedProcessing}>
                Clear Completed
              </Button>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <AnimatePresence>
                {activeProcessing.map((processing) => (
                  <motion.div
                    key={processing.fileId}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    className="border rounded-lg p-4 space-y-2"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-medium">{processing.filename}</span>
                      <Badge 
                        variant={
                          processing.status === 'processing' ? 'default' :
                          processing.status === 'completed' ? 'success' :
                          processing.status === 'failed' ? 'destructive' : 'secondary'
                        }
                      >
                        {processing.status}
                      </Badge>
                    </div>

                    {processing.stage && (
                      <p className="text-sm text-muted-foreground">
                        Stage: {processing.stage}
                      </p>
                    )}

                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <motion.div
                        className="bg-purple-500 h-2 rounded-full"
                        initial={{ width: 0 }}
                        animate={{ width: `${processing.progress}%` }}
                        transition={{ duration: 0.5 }}
                      />
                    </div>

                    {processing.error && (
                      <p className="text-sm text-red-600">{processing.error}</p>
                    )}
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          </CardContent>
        </Card>
      )}

      {/* No Active Tasks */}
      {activeExecutions.length === 0 && activeProcessing.length === 0 && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-8 text-center">
            <Clock className="w-12 h-12 text-muted-foreground mb-4" />
            <h3 className="font-medium mb-2">No Active Tasks</h3>
            <p className="text-sm text-muted-foreground">
              Start an agent execution or upload data to see real-time progress here.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
