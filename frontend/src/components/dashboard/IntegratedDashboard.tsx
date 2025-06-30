import React, { useState, useCallback } from 'react'
import { motion } from 'framer-motion'
import { 
  Brain, 
  MessageSquare, 
  Upload, 
  BarChart3,
  Activity,
  Settings,
  Bell,
  Zap
} from 'lucide-react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { EnhancedChatInterface } from '@/components/chat/EnhancedChatInterface'
import { AgentExecutionComponent } from '@/components/agents/AgentExecution'
import { EnhancedDataProcessing } from '@/components/data/EnhancedDataProcessing'
import { RealTimeStatusDashboard } from '@/components/status/RealTimeStatusDashboard'
import { DataVisualization } from '@/components/insights/DataVisualization'
import { useToast } from '@/components/ui/notification'
import { useHealthCheck } from '@/hooks/api'
import { useRealTimeStatus } from '@/hooks/useRealTimeStatus'

export function IntegratedDashboard() {
  const [activeTab, setActiveTab] = useState('chat')
  const [sessionId, setSessionId] = useState<string>()
  const [notifications, setNotifications] = useState<any[]>([])
  const [analysisResults, setAnalysisResults] = useState<any[]>([])
  
  const { success, info } = useToast()
  const healthCheck = useHealthCheck()
  const realTimeStatus = useRealTimeStatus({ sessionId })

  const handleNewSession = useCallback((newSessionId: string) => {
    setSessionId(newSessionId)
    info('New session created', {
      message: `Session ID: ${newSessionId.slice(0, 8)}...`
    })
  }, [info])

  const handleFileProcessed = useCallback((file: any) => {
    success('File processed successfully!', {
      message: `${file.filename} is ready for analysis`
    })
    // Switch to data tab to show results
    setActiveTab('data')
  }, [success])

  const handleExecutionComplete = useCallback((result: any) => {
    success('Agent execution completed!', {
      message: 'Check the results in the execution panel'
    })
    setNotifications(prev => [...prev, {
      id: Date.now(),
      type: 'execution_complete',
      message: 'Agent execution finished',
      timestamp: new Date().toISOString(),
      result
    }])
  }, [success])

  const handleAnalysisComplete = useCallback((results: any) => {
    success('Data analysis completed!', {
      message: 'Analysis results are now available'
    })
    
    // Store analysis results for visualization
    setAnalysisResults(prev => [...prev, {
      ...results,
      timestamp: new Date().toISOString(),
      id: Math.random().toString(36).substring(7)
    }])
    
    setNotifications(prev => [...prev, {
      id: Date.now(),
      type: 'analysis_complete',
      message: 'Data analysis finished',
      timestamp: new Date().toISOString(),
      results
    }])
    
    // Switch to insights tab to show results
    setActiveTab('insights')
  }, [success])

  const clearNotifications = useCallback(() => {
    setNotifications([])
  }, [])

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 border-b shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <Brain className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold">Enterprise Insights Copilot</h1>
                <p className="text-xs text-gray-500">AI-Powered Business Intelligence Platform</p>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              {/* System Status */}
              <div className="flex items-center gap-2">
                {healthCheck.data?.status === 'healthy' && (
                  <Badge variant="outline" className="border-green-500 text-green-700">
                    <Activity className="w-3 h-3 mr-1" />
                    System Healthy
                  </Badge>
                )}
                
                {/* Real-time Status Compact */}
                <RealTimeStatusDashboard sessionId={sessionId} compact={true} />
                
                {sessionId && (
                  <Badge variant="outline">
                    Session: {sessionId.slice(0, 8)}...
                  </Badge>
                )}
              </div>
              
              {/* Notifications */}
              <div className="relative">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={clearNotifications}
                  className="relative"
                >
                  <Bell className="w-4 h-4" />
                  {notifications.length > 0 && (
                    <Badge className="absolute -top-1 -right-1 h-5 w-5 p-0 text-xs">
                      {notifications.length}
                    </Badge>
                  )}
                </Button>
              </div>
              
              <Button variant="ghost" size="sm">
                <Settings className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          {/* Tab Navigation */}
          <TabsList className="grid w-full grid-cols-5 lg:w-fit lg:grid-cols-5">
            <TabsTrigger value="chat" className="flex items-center gap-2">
              <MessageSquare className="w-4 h-4" />
              Chat Assistant
            </TabsTrigger>
            <TabsTrigger value="agents" className="flex items-center gap-2">
              <Brain className="w-4 h-4" />
              AI Agents
            </TabsTrigger>
            <TabsTrigger value="data" className="flex items-center gap-2">
              <Upload className="w-4 h-4" />
              Data Processing
            </TabsTrigger>
            <TabsTrigger value="status" className="flex items-center gap-2">
              <Activity className="w-4 h-4" />
              Status
              {realTimeStatus.agentExecutions.size > 0 && (
                <Badge variant="secondary" className="ml-1 h-5 w-5 p-0 text-xs">
                  {realTimeStatus.agentExecutions.size}
                </Badge>
              )}
            </TabsTrigger>
            <TabsTrigger value="insights" className="flex items-center gap-2">
              <BarChart3 className="w-4 h-4" />
              Insights
            </TabsTrigger>
          </TabsList>

          {/* Tab Content */}
          <div className="space-y-6">
            {/* Chat Assistant Tab */}
            <TabsContent value="chat" className="space-y-6">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
              >
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  {/* Main Chat Interface */}
                  <div className="lg:col-span-2">
                    <EnhancedChatInterface
                      sessionId={sessionId}
                      onNewSession={handleNewSession}
                      height="600px"
                    />
                  </div>
                  
                  {/* Quick Actions & Info */}
                  <div className="space-y-4">
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-lg">Quick Actions</CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-3">
                        <Button 
                          variant="outline" 
                          className="w-full justify-start"
                          onClick={() => setActiveTab('data')}
                        >
                          <Upload className="w-4 h-4 mr-2" />
                          Upload Data File
                        </Button>
                        <Button 
                          variant="outline" 
                          className="w-full justify-start"
                          onClick={() => setActiveTab('agents')}
                        >
                          <Brain className="w-4 h-4 mr-2" />
                          Execute AI Agent
                        </Button>
                        <Button 
                          variant="outline" 
                          className="w-full justify-start"
                          onClick={() => setActiveTab('insights')}
                        >
                          <BarChart3 className="w-4 h-4 mr-2" />
                          View Insights
                        </Button>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardHeader>
                        <CardTitle className="text-lg">Recent Activity</CardTitle>
                      </CardHeader>
                      <CardContent>
                        {notifications.length === 0 ? (
                          <p className="text-sm text-gray-500">No recent activity</p>
                        ) : (
                          <div className="space-y-2">
                            {notifications.slice(0, 5).map((notification) => (
                              <div 
                                key={notification.id}
                                className="text-sm p-2 bg-gray-50 dark:bg-gray-800 rounded"
                              >
                                <div className="flex items-center gap-2">
                                  <Zap className="w-3 h-3 text-blue-500" />
                                  <span className="font-medium">{notification.message}</span>
                                </div>
                                <p className="text-xs text-gray-500 mt-1">
                                  {new Date(notification.timestamp).toLocaleTimeString()}
                                </p>
                              </div>
                            ))}
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  </div>
                </div>
              </motion.div>
            </TabsContent>

            {/* AI Agents Tab */}
            <TabsContent value="agents" className="space-y-6">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
              >
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* Agent Execution */}
                  <AgentExecutionComponent
                    sessionId={sessionId}
                    onExecutionComplete={handleExecutionComplete}
                    className="h-fit"
                  />
                  
                  {/* Agent Results & History */}
                  <Card>
                    <CardHeader>
                      <CardTitle>Execution History</CardTitle>
                    </CardHeader>
                    <CardContent>
                      {notifications.filter(n => n.type === 'execution_complete').length === 0 ? (
                        <div className="text-center py-8 text-gray-500">
                          <Brain className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                          <p>No agent executions yet</p>
                          <p className="text-sm">Execute an agent to see results here</p>
                        </div>
                      ) : (
                        <div className="space-y-3">
                          {notifications
                            .filter(n => n.type === 'execution_complete')
                            .slice(0, 5)
                            .map((execution) => (
                              <div 
                                key={execution.id}
                                className="border rounded-lg p-3"
                              >
                                <div className="flex items-center justify-between mb-2">
                                  <Badge variant="outline">Completed</Badge>
                                  <span className="text-xs text-gray-500">
                                    {new Date(execution.timestamp).toLocaleString()}
                                  </span>
                                </div>
                                <p className="text-sm font-medium">{execution.message}</p>
                                {execution.result && (
                                  <div className="mt-2 p-2 bg-gray-50 dark:bg-gray-800 rounded text-xs">
                                    <pre className="whitespace-pre-wrap">
                                      {typeof execution.result === 'string' 
                                        ? execution.result 
                                        : JSON.stringify(execution.result, null, 2)
                                      }
                                    </pre>
                                  </div>
                                )}
                              </div>
                            ))
                          }
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </div>
              </motion.div>
            </TabsContent>

            {/* Data Processing Tab */}
            <TabsContent value="data" className="space-y-6">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
              >
                <EnhancedDataProcessing
                  onFileProcessed={handleFileProcessed}
                  onAnalysisComplete={handleAnalysisComplete}
                />
              </motion.div>
            </TabsContent>

            {/* Real-Time Status Tab */}
            <TabsContent value="status" className="space-y-6">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
              >
                <RealTimeStatusDashboard sessionId={sessionId} />
              </motion.div>
            </TabsContent>

            {/* Insights Tab */}
            <TabsContent value="insights" className="space-y-6">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
              >
                <DataVisualization 
                  analysisResults={analysisResults}
                  sessionId={sessionId}
                />
              </motion.div>
            </TabsContent>
          </div>
        </Tabs>
      </main>
    </div>
  )
}
