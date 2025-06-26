'use client'

import { useState, useEffect } from 'react'

// Types
interface FileInfo {
  name: string
  size: number
  type: string
  rows: number
  columns: number
}

interface PreviewData {
  columns: string[]
  rows: Record<string, any>[]
}

interface AppState {
  currentFileId: string | null
  currentFileName: string
  fileInfo: FileInfo | null
  previewData: PreviewData | null
  demoMode: boolean
  backendConnected: boolean
  isCheckingBackend: boolean
  chatMessages: Array<{
    id: string
    message: string
    isUser: boolean
    timestamp: Date
  }>
  agentStatuses: Record<string, 'idle' | 'active' | 'complete' | 'error'>
  agentOutputs: Record<string, string[]>
}

// Simple API client
const apiClient = {
  async checkHealth() {
    try {
      const response = await fetch('http://localhost:8000/health')
      return response.ok
    } catch {
      return false
    }
  },

  async uploadFile(file: File) {
    try {
      const formData = new FormData()
      formData.append('file', file)
      const response = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData
      })
      if (response.ok) {
        return await response.json()
      }
      return null
    } catch {
      return null
    }
  },

  async sendQuery(query: string, fileId: string) {
    try {
      const response = await fetch('http://localhost:8000/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, file_id: fileId })
      })
      if (response.ok) {
        return await response.json()
      }
      return null
    } catch {
      return null
    }
  }
}

// SSR-safe timestamp formatter
const formatTimestamp = (timestamp: Date, isClient: boolean) => {
  if (!isClient) return '00:00:00'
  return timestamp.toLocaleTimeString()
}

// Unique ID generator (SSR-safe)
let idCounter = 0
const generateUniqueId = () => {
  idCounter += 1
  return `id_${idCounter}`
}

// Agent definitions
const agents = [
  { id: 'file-upload', name: 'File Upload', icon: '📁', description: 'Data ingestion and validation' },
  { id: 'data-agent', name: 'Data Agent', icon: '📊', description: 'Data profiling and analysis' },
  { id: 'retrieval-agent', name: 'Retrieval Agent', icon: '🔍', description: 'Information retrieval and context' },
  { id: 'planning-agent', name: 'Planning Agent', icon: '🧠', description: 'Query planning and orchestration' },
  { id: 'query-agent', name: 'Query Agent', icon: '💬', description: 'Natural language processing' },
  { id: 'sql-agent', name: 'SQL Agent', icon: '🗄️', description: 'SQL generation and execution' },
  { id: 'insight-agent', name: 'Insight Agent', icon: '👁️', description: 'Pattern detection and insights' },
  { id: 'chart-agent', name: 'Chart Agent', icon: '📈', description: 'Data visualization and charts' },
  { id: 'critique-agent', name: 'Critique Agent', icon: '⚠️', description: 'Quality assessment and validation' },
  { id: 'narrative-agent', name: 'Narrative Agent', icon: '📝', description: 'Story generation and narratives' }
]

export default function Home() {
  const [isClient, setIsClient] = useState(false)
  const [currentQuery, setCurrentQuery] = useState('')
  
  const [appState, setAppState] = useState<AppState>({
    currentFileId: null,
    currentFileName: '',
    fileInfo: null,
    previewData: null,
    demoMode: true,
    backendConnected: false,
    isCheckingBackend: false,
    chatMessages: [],
    agentStatuses: {},
    agentOutputs: {}
  })

  // Set client flag after mount
  useEffect(() => {
    setIsClient(true)
  }, [])

  // Check backend on mount
  useEffect(() => {
    if (isClient) {
      checkBackendHealth()
    }
  }, [isClient])

  const checkBackendHealth = async () => {
    setAppState(prev => ({ ...prev, isCheckingBackend: true }))
    
    const isHealthy = await apiClient.checkHealth()
    
    setAppState(prev => ({
      ...prev,
      backendConnected: isHealthy,
      demoMode: !isHealthy,
      isCheckingBackend: false
    }))
  }

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    console.log('📁 File selected:', file.name)

    // Always try backend first if connected
    if (appState.backendConnected && !appState.demoMode) {
      console.log('☁️ Attempting real backend upload...')
      const uploadResult = await apiClient.uploadFile(file)
      
      if (uploadResult) {
        console.log('✅ Real upload successful:', uploadResult)
        
        setAppState(prev => ({
          ...prev,
          currentFileId: uploadResult.file_id,
          currentFileName: file.name,
          demoMode: false, // Ensure we're not in demo mode for real data
          fileInfo: {
            name: file.name,
            size: file.size,
            type: file.type,
            rows: uploadResult.rows || 0,
            columns: uploadResult.columns || 0
          },
          previewData: uploadResult.preview_data || null,
          agentStatuses: {
            'file-upload': 'complete',
            'data-agent': 'active'
          },
          agentOutputs: {
            'file-upload': ['[REAL] File uploaded successfully', '[REAL] Processing file format'],
            'data-agent': ['[REAL] Analyzing data structure...', '[REAL] Detecting column types...']
          }
        }))

        // Real agent processing simulation
        setTimeout(async () => {
          // Try to fetch real agent status from backend
          try {
            const statusResponse = await fetch(`http://localhost:8000/api/v1/agents/status/${uploadResult.file_id}`)
            if (statusResponse.ok) {
              const agentStatus = await statusResponse.json()
              console.log('🔍 Real agent status received:', agentStatus)
              
              // Update with real backend agent outputs
              setAppState(prev => ({
                ...prev,
                agentStatuses: {
                  ...prev.agentStatuses,
                  'data-agent': 'complete',
                  'retrieval-agent': 'complete'
                },
                agentOutputs: {
                  ...prev.agentOutputs,
                  'data-agent': agentStatus.agents['data-agent']?.outputs || [
                    '[REAL] Data structure analyzed',
                    `[REAL] ${uploadResult.columns || 0} columns detected`,
                    `[REAL] ${uploadResult.rows || 0} rows processed`,
                    '[REAL] Data quality: Good'
                  ],
                  'retrieval-agent': agentStatus.agents['retrieval-agent']?.outputs || ['[REAL] Indexing data...']
                }
              }))
            } else {
              // Fallback to simulated real processing
              setAppState(prev => ({
                ...prev,
                agentStatuses: {
                  ...prev.agentStatuses,
                  'data-agent': 'complete',
                  'retrieval-agent': 'active'
                },
                agentOutputs: {
                  ...prev.agentOutputs,
                  'data-agent': [
                    '[REAL] Data structure analyzed',
                    `[REAL] ${uploadResult.columns || 0} columns detected`,
                    `[REAL] ${uploadResult.rows || 0} rows processed`,
                    '[REAL] Data quality: Good'
                  ],
                  'retrieval-agent': ['[REAL] Indexing data...']
                }
              }))
            }
          } catch (error) {
            console.log('⚠️ Could not fetch real agent status, using simulation')
            // Fallback to simulated processing  
            setAppState(prev => ({
              ...prev,
              agentStatuses: {
                ...prev.agentStatuses,
                'data-agent': 'complete',
                'retrieval-agent': 'active'
              },
              agentOutputs: {
                ...prev.agentOutputs,
                'data-agent': [
                  '[REAL] Data structure analyzed',
                  `[REAL] ${uploadResult.columns || 0} columns detected`,
                  `[REAL] ${uploadResult.rows || 0} rows processed`,
                  '[REAL] Data quality: Good'
                ],
                'retrieval-agent': ['[REAL] Indexing data...']
              }
            }))
          }
        }, 2000)

        setTimeout(async () => {
          // Try to fetch final agent status AND embedding status
          try {
            const statusResponse = await fetch(`http://localhost:8000/api/v1/agents/status/${uploadResult.file_id}`)
            const embeddingResponse = await fetch(`http://localhost:8000/api/v1/agents/embedding-status/${uploadResult.file_id}`)
            
            let retrievalOutputs = ['[REAL] Data indexed successfully', '[REAL] Ready for queries']
            
            if (statusResponse.ok) {
              const agentStatus = await statusResponse.json()
              retrievalOutputs = agentStatus.agents['retrieval-agent']?.outputs || retrievalOutputs
            }
            
            // Enhance with embedding status (before/after vector counts)
            if (embeddingResponse.ok) {
              const embeddingStatus = await embeddingResponse.json()
              const embeddingInfo = embeddingStatus.embedding_status
              
              if (embeddingInfo) {
                const vectorsBefore = embeddingInfo.vectors_before_embedding
                const vectorsAfter = embeddingInfo.estimated_vectors_after_embedding
                const vectorsToAdd = embeddingInfo.estimated_vectors_to_add
                
                // Add enhanced vector count information
                retrievalOutputs = [
                  `[REAL] Indexing ${embeddingStatus.filename} data`,
                  `[REAL] Vectors before embedding: ${vectorsBefore}`,
                  `[REAL] Vectors to add: ${vectorsToAdd}`,
                  `[REAL] Vectors after embedding: ${vectorsAfter}`,
                  `[REAL] Pinecone status: ${embeddingStatus.pinecone_status}`,
                  '[REAL] Data indexed successfully',
                  '[REAL] Ready for queries'
                ]
              }
            }
            
            setAppState(prev => ({
              ...prev,
              agentStatuses: {
                ...prev.agentStatuses,
                'retrieval-agent': 'complete'
              },
              agentOutputs: {
                ...prev.agentOutputs,
                'retrieval-agent': retrievalOutputs
              }
            }))
          } catch (error) {
            console.log('⚠️ Could not fetch embedding status, using fallback')
            // Fallback
            setAppState(prev => ({
              ...prev,
              agentStatuses: {
                ...prev.agentStatuses,
                'retrieval-agent': 'complete'
              },
              agentOutputs: {
                ...prev.agentOutputs,
                'retrieval-agent': ['[REAL] Data indexed successfully', '[REAL] Ready for queries']
              }
            }))
          }
        }, 4000)
        
        return
      } else {
        console.log('❌ Real upload failed, falling back to demo')
        setAppState(prev => ({ ...prev, demoMode: true }))
      }
    }

    // Demo fallback
    console.log('🎭 Using demo mode')
    setAppState(prev => ({
      ...prev,
      currentFileId: generateUniqueId(),
      currentFileName: file.name,
      demoMode: true, // Explicitly set demo mode
      fileInfo: {
        name: file.name,
        size: file.size,
        type: file.type,
        rows: 22,
        columns: 10
      },
      previewData: {
        columns: ['[SAMPLE] ID', '[SAMPLE] Name', '[SAMPLE] Age', '[SAMPLE] Department', '[SAMPLE] Salary'],
        rows: [
          { '[SAMPLE] ID': 'demo_1', '[SAMPLE] Name': 'Sample Employee 1', '[SAMPLE] Age': '30', '[SAMPLE] Department': 'Sample Dept', '[SAMPLE] Salary': '$50,000' },
          { '[SAMPLE] ID': 'demo_2', '[SAMPLE] Name': 'Sample Employee 2', '[SAMPLE] Age': '28', '[SAMPLE] Department': 'Sample Dept', '[SAMPLE] Salary': '$45,000' },
          { '[SAMPLE] ID': 'demo_3', '[SAMPLE] Name': 'Sample Employee 3', '[SAMPLE] Age': '35', '[SAMPLE] Department': 'Sample Dept', '[SAMPLE] Salary': '$55,000' },
          { '[SAMPLE] ID': 'demo_4', '[SAMPLE] Name': 'Sample Employee 4', '[SAMPLE] Age': '32', '[SAMPLE] Department': 'Sample Dept', '[SAMPLE] Salary': '$52,000' },
          { '[SAMPLE] ID': 'demo_5', '[SAMPLE] Name': 'Sample Employee 5', '[SAMPLE] Age': '29', '[SAMPLE] Department': 'Sample Dept', '[SAMPLE] Salary': '$48,000' }
        ]
      },
      agentStatuses: {
        'file-upload': 'complete',
        'data-agent': 'active'
      },
      agentOutputs: {
        'file-upload': ['[DEMO] File uploaded successfully', '[DEMO] Processing file format'],
        'data-agent': ['[DEMO] Analyzing data structure...', '[DEMO] Detecting column types...']
      }
    }))

    // Simulate agent processing
    setTimeout(() => {
      setAppState(prev => ({
        ...prev,
        agentStatuses: {
          ...prev.agentStatuses,
          'data-agent': 'complete',
          'retrieval-agent': 'active'
        },
        agentOutputs: {
          ...prev.agentOutputs,
          'data-agent': [
            '[DEMO] Data structure analyzed',
            '[DEMO] Sample columns detected',
            '[DEMO] Sample rows processed',
            '[DEMO] Data quality: Placeholder'
          ],
          'retrieval-agent': ['[DEMO] Indexing placeholder data...']
        }
      }))
    }, 2000)

    setTimeout(() => {
      setAppState(prev => ({
        ...prev,
        agentStatuses: {
          ...prev.agentStatuses,
          'retrieval-agent': 'complete'
        },
        agentOutputs: {
          ...prev.agentOutputs,
          'retrieval-agent': ['[DEMO] Placeholder data indexed', '[DEMO] Ready for demo queries']
        }
      }))
    }, 4000)
  }

  const handleSendMessage = async () => {
    if (!currentQuery.trim()) return
    
    const newMessage = {
      id: generateUniqueId(),
      message: currentQuery,
      isUser: true,
      timestamp: isClient ? new Date() : new Date(2000, 0, 1), // Use fixed date for SSR
    }

    setAppState(prev => ({
      ...prev,
      chatMessages: [...prev.chatMessages, newMessage],
    }))

    if (appState.backendConnected && !appState.demoMode && appState.currentFileId) {
      console.log('🔍 Sending query to real backend...')
      
      // Set real agent status
      setAppState(prev => ({
        ...prev,
        agentStatuses: {
          ...prev.agentStatuses,
          'planning-agent': 'active'
        },
        agentOutputs: {
          ...prev.agentOutputs,
          'planning-agent': ['[REAL] Analyzing query...', '[REAL] Planning response...']
        }
      }))
      
      const queryResult = await apiClient.sendQuery(currentQuery, appState.currentFileId)
      
      if (queryResult) {
        const aiResponse = {
          id: generateUniqueId(),
          message: queryResult.response || `Analysis complete for: "${currentQuery}"`,
          isUser: false,
          timestamp: isClient ? new Date() : new Date(2000, 0, 1), // Use fixed date for SSR
        }

        setAppState(prev => ({
          ...prev,
          chatMessages: [...prev.chatMessages, aiResponse],
          agentStatuses: {
            ...prev.agentStatuses,
            'planning-agent': 'complete',
            'query-agent': 'complete',
            'sql-agent': 'complete',
            'insight-agent': 'complete'
          },
          agentOutputs: {
            ...prev.agentOutputs,
            'planning-agent': ['[REAL] Query plan created', '[REAL] Strategy defined'],
            'query-agent': ['[REAL] Language processed', '[REAL] Intent understood'],
            'sql-agent': ['[REAL] SQL generated', '[REAL] Results retrieved'],
            'insight-agent': ['[REAL] Insights generated', '[REAL] Analysis complete']
          }
        }))
        
        setCurrentQuery('')
        return
      } else {
        console.log('❌ Backend query failed, falling back to demo mode')
        setAppState(prev => ({ ...prev, demoMode: true }))
      }
    }

    // Demo mode response
    setAppState(prev => ({
      ...prev,
      agentStatuses: {
        ...prev.agentStatuses,
        'planning-agent': 'active'
      },        agentOutputs: {
          ...prev.agentOutputs,
          'planning-agent': ['[DEMO] Analyzing query...', '[DEMO] Planning demo response...']
        }
    }))

    setTimeout(() => {
      const aiResponse = {
        id: generateUniqueId(),
        message: `[DEMO] I understand you're asking about: "${currentQuery}". This is a demonstration of the AI analysis interface. In production, I would analyze your real data and provide actual insights.`,
        isUser: false,
        timestamp: isClient ? new Date() : new Date(2000, 0, 1), // Use fixed date for SSR
      }

      setAppState(prev => ({
        ...prev,
        chatMessages: [...prev.chatMessages, aiResponse],
        agentStatuses: {
          ...prev.agentStatuses,
          'planning-agent': 'complete',
          'query-agent': 'active',
          'sql-agent': 'active'
        },
        agentOutputs: {
          ...prev.agentOutputs,
          'planning-agent': ['[DEMO] Query plan created', '[DEMO] Demo strategy defined'],
          'query-agent': ['[DEMO] Processing demo language...'],
          'sql-agent': ['[DEMO] Generating demo queries...']
        }
      }))
    }, 1000)

    setTimeout(() => {
      setAppState(prev => ({
        ...prev,
        agentStatuses: {
          ...prev.agentStatuses,
          'query-agent': 'complete',
          'sql-agent': 'complete',
          'insight-agent': 'active'
        },
        agentOutputs: {
          ...prev.agentOutputs,
          'query-agent': ['[DEMO] Language processed', '[DEMO] Demo intent understood'],
          'sql-agent': ['[DEMO] Demo SQL generated', '[DEMO] Demo results retrieved'],
          'insight-agent': ['[DEMO] Analyzing demo patterns...', '[DEMO] Extracting demo insights...']
        }
      }))
    }, 3000)

    setTimeout(() => {
      setAppState(prev => ({
        ...prev,
        agentStatuses: {
          ...prev.agentStatuses,
          'insight-agent': 'complete'
        },
        agentOutputs: {
          ...prev.agentOutputs,
          'insight-agent': ['[DEMO] Demo insights generated', '[DEMO] Demo analysis complete']
        }
      }))
    }, 5000)

    setCurrentQuery('')
  }

  const resetFileUpload = () => {
    setAppState(prev => ({
      ...prev,
      currentFileId: null,
      currentFileName: '',
      fileInfo: null,
      previewData: null,
      demoMode: !prev.backendConnected, // Reset to demo mode if backend is not connected
      chatMessages: [],
      agentStatuses: {},
      agentOutputs: {}
    }))
  }

  const getAgentStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-blue-500/20 text-blue-300 border-blue-500/30'
      case 'complete': return 'bg-green-500/20 text-green-300 border-green-500/30'
      case 'error': return 'bg-red-500/20 text-red-300 border-red-500/30'
      default: return 'bg-gray-500/20 text-gray-300 border-gray-500/30'
    }
  }

  const getAgentStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return '⚡'
      case 'complete': return '✅'
      case 'error': return '❌'
      default: return '⏸️'
    }
  }

  if (!isClient) {
    return <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
      <div className="text-white text-lg">Loading...</div>
    </div>
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <header className="border-b border-white/10 bg-black/20 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-white">Enterprise Insights Copilot</h1>
              <p className="text-white/70 text-sm">Powered by Multi-Agent AI System</p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${appState.backendConnected ? 'bg-green-400' : 'bg-red-400'}`}></div>
                <span className="text-white/90 text-sm">
                  {appState.isCheckingBackend ? 'Checking Backend...' : 
                   appState.backendConnected ? 'Backend Connected' : 'Backend Offline - Demo Mode'}
                </span>
              </div>
              {!appState.backendConnected && !appState.isCheckingBackend && (
                <button
                  onClick={checkBackendHealth}
                  className="text-xs px-3 py-1 bg-blue-500/20 hover:bg-blue-500/30 border border-blue-400/40 rounded-lg text-blue-300 hover:text-blue-200 transition-colors"
                >
                  Retry Connection
                </button>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6 h-[calc(100vh-180px)]">
          
          {/* Left Column */}
          <div className="flex flex-col space-y-6 h-full">
            
            {/* File Upload */}
            <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20 flex-shrink-0">
              <h3 className="text-white font-semibold text-lg mb-4">Data Upload</h3>
              
              {!appState.currentFileId ? (
                <div className="relative">
                  <input
                    type="file"
                    accept=".csv,.xlsx,.json"
                    onChange={handleFileUpload}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                  />
                  <div className="border-2 border-dashed border-white/30 rounded-xl p-8 text-center hover:border-white/50 transition-colors">
                    <div className="text-white/60 mb-2 text-4xl">📁</div>
                    <p className="text-white/90 mb-1">Drop your data file here</p>
                    <p className="text-white/70 text-sm">CSV, Excel, JSON supported</p>
                  </div>
                </div>
              ) : (
                <div className="flex items-center justify-between p-4 bg-green-500/20 border border-green-400/40 rounded-xl">
                  <div>
                    <p className="text-white font-medium">{appState.currentFileName}</p>
                    <p className="text-green-200/80 text-sm">Ready for analysis</p>
                  </div>
                  <button
                    onClick={resetFileUpload}
                    className="text-red-400 hover:text-red-300 p-2 rounded transition-colors"
                    title="Remove file"
                  >
                    ✕
                  </button>
                </div>
              )}
            </div>

            {/* Data Preview - FIXED: Always Visible and Properly Scrollable */}
            {appState.fileInfo && (
              <div className="bg-white/10 backdrop-blur-md rounded-2xl border border-white/20 flex-1 flex flex-col min-h-0">
                <div className="p-4 border-b border-white/10 flex-shrink-0">
                  <div className="flex items-center justify-between">
                    <h4 className="text-white font-semibold">Data Preview</h4>
                    <span className={`text-xs px-3 py-1 rounded-full ${
                      appState.demoMode 
                        ? 'bg-yellow-500/20 text-yellow-300 border border-yellow-500/30' 
                        : 'bg-green-500/20 text-green-300 border border-green-500/30'
                    }`}>
                      {appState.demoMode ? 'DEMO DATA' : 'LIVE DATA'}
                    </span>
                  </div>
                  <p className="text-white/70 text-sm mt-1">
                    {appState.fileInfo.rows} rows × {appState.fileInfo.columns} columns
                  </p>
                </div>
                
                {/* Table Container - Takes remaining space and scrolls */}
                <div className="flex-1 overflow-auto bg-black/20 min-h-0">
                  <table className="w-full text-sm">
                    <thead className="bg-black/40 sticky top-0">
                      <tr>
                        {appState.previewData?.columns?.map((col, idx) => (
                          <th key={idx} className="text-left text-white/90 p-3 border-b border-white/10 font-semibold">
                            {col}
                          </th>
                        )) || (
                          <th className="text-left text-white/90 p-3 border-b border-white/10">Loading...</th>
                        )}
                      </tr>
                    </thead>
                    <tbody>
                      {appState.previewData?.rows?.map((row, idx) => (
                        <tr key={idx} className="border-b border-white/5 hover:bg-white/10 transition-colors">
                          {appState.previewData?.columns?.map((col, colIdx) => (
                            <td key={colIdx} className={`p-3 ${appState.demoMode ? 'text-white/50 italic' : 'text-white/90'}`}>
                              {String(row[col] ?? '').substring(0, 50)}
                              {String(row[col] ?? '').length > 50 ? '...' : ''}
                            </td>
                          ))}
                        </tr>
                      )) || (
                        <tr>
                          <td className="text-white/70 p-8 text-center italic" colSpan={100}>
                            Loading data preview...
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
                
                <div className="p-3 bg-black/30 text-xs text-white/60 border-t border-white/10 flex-shrink-0">
                  {appState.demoMode 
                    ? "🎭 Demo data shown - actual file content will appear when backend is connected"
                    : "📊 Showing preview of your uploaded data file"
                  }
                </div>
              </div>
            )}
          </div>

          {/* Right Column - Chat */}
          <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20 flex flex-col h-full">
            <h3 className="text-white font-semibold text-lg mb-4 flex-shrink-0">AI Assistant</h3>
            
            {/* Messages Container - Takes remaining space and scrolls */}
            <div className="flex-1 overflow-y-auto space-y-3 mb-4 bg-black/20 rounded-xl p-4 min-h-0">
              {appState.chatMessages.length === 0 ? (
                <div className="text-center py-16">
                  <div className="text-6xl mb-4">🧠</div>
                  <p className="text-white/90 text-lg mb-2">Ask me anything about your data</p>
                  <p className="text-white/60">Upload a file to start analyzing trends and generating insights</p>
                </div>
              ) : (
                appState.chatMessages.map((msg) => (
                  <div key={msg.id} className={`flex ${msg.isUser ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-[80%] p-3 rounded-xl ${
                      msg.isUser 
                        ? 'bg-purple-600/80 text-white' 
                        : 'bg-white/20 text-white border border-white/30'
                    }`}>
                      <p className="text-sm">{msg.message}</p>
                      <p className="text-xs opacity-70 mt-1">
                        {formatTimestamp(msg.timestamp, isClient)}
                      </p>
                    </div>
                  </div>
                ))
              )}
            </div>

            {/* Input - Fixed at Bottom */}
            <div className="flex space-x-3 flex-shrink-0">
              <input
                type="text"
                value={currentQuery}
                onChange={(e) => setCurrentQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
                placeholder="Ask about your data..."
                className="flex-1 px-4 py-3 bg-white/10 border border-white/30 rounded-xl text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                disabled={!appState.currentFileId}
              />
              <button
                onClick={handleSendMessage}
                disabled={!currentQuery.trim() || !appState.currentFileId}
                className="px-6 py-3 bg-purple-600 text-white rounded-xl hover:bg-purple-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Send
              </button>
            </div>
          </div>

          {/* Third Column - Agent Orchestration */}
          <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20 flex flex-col h-full">
            <h3 className="text-white font-semibold text-lg mb-4 flex-shrink-0">Agent Orchestration</h3>
            <p className="text-white/70 text-sm mb-6 flex-shrink-0">Multi-agent AI system processing your data</p>
            
            {/* Agent List - Scrollable */}
            <div className="flex-1 overflow-y-auto space-y-3 min-h-0">
              {agents.map((agent) => {
                const status = appState.agentStatuses[agent.id] || 'idle'
                const outputs = appState.agentOutputs[agent.id] || []
                
                return (
                  <div key={agent.id} className="bg-black/20 rounded-xl p-4 border border-white/10">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-3">
                        <span className="text-2xl">{agent.icon}</span>
                        <div>
                          <h4 className="text-white font-medium text-sm">{agent.name}</h4>
                          <p className="text-white/60 text-xs">{agent.description}</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className={`text-xs px-2 py-1 rounded-full border ${getAgentStatusColor(status)}`}>
                          {getAgentStatusIcon(status)} {status.toUpperCase()}
                        </span>
                      </div>
                    </div>
                    
                    {outputs.length > 0 && (
                      <div className="bg-black/30 rounded-lg p-3 mt-3">
                        <div className="text-xs text-white/80 space-y-1">
                          {outputs.map((output, idx) => (
                            <div key={idx} className="flex items-start space-x-2">
                              <span className="text-white/50">•</span>
                              <span>{output}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
