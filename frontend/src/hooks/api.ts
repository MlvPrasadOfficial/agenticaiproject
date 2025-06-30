import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api-client'
import { 
  HealthCheck, 
  FileUploadResponse, 
  DataPreview, 
  WorkflowStatus,
  QueryRequest,
  QueryResponse,
  validateSchema,
  HealthCheckSchema,
  FileUploadResponseSchema,
  DataPreviewSchema,
  WorkflowStatusSchema,
  QueryResponseSchema,
} from '@/lib/schemas'

// Additional schemas for agent operations
export interface AgentExecutionRequest {
  agent_type: string;
  query: string;
  session_id?: string;
  data_source?: string;
  parameters?: Record<string, any>;
}

export interface AgentExecutionResponse {
  execution_id: string;
  agent_type: string;
  status: string;
  session_id: string;
  timestamp: string;
  estimated_duration: number;
}

export interface ConversationMessage {
  id: string;
  session_id: string;
  message: string;
  response: string;
  timestamp: string;
  agent_type?: string;
  metadata?: Record<string, any>;
}

export interface ConversationRequest {
  session_id: string;
  message: string;
  context?: Record<string, any>;
}

export interface SessionRequest {
  user_id?: string;
  session_name?: string;
  metadata?: Record<string, any>;
}

export interface Session {
  session_id: string;
  user_id?: string;
  session_name?: string;
  created_at: string;
  updated_at: string;
  metadata?: Record<string, any>;
}

// Additional interfaces for real-time status tracking
export interface ExecutionStatus {
  execution_id: string;
  agent_type: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  message: string;
  timestamp: string;
  result?: Record<string, any>;
  error?: string;
}

export interface StatusUpdate {
  id: string;
  type: 'agent_execution' | 'workflow';
  status: string;
  progress?: number;
  message?: string;
  timestamp: string;
  metadata?: Record<string, any>;
}

// Query keys for consistent caching
export const queryKeys = {
  health: ['health'] as const,
  files: ['files'] as const,
  file: (id: string) => ['files', id] as const,
  dataPreview: (fileId: string, page: number = 1) => ['data-preview', fileId, page] as const,
  workflows: ['workflows'] as const,
  workflow: (id: string) => ['workflows', id] as const,
  queries: ['queries'] as const,
  query: (id: string) => ['queries', id] as const,
  // New agent-related keys
  sessions: ['sessions'] as const,
  session: (id: string) => ['sessions', id] as const,
  conversation: (sessionId: string) => ['conversations', sessionId] as const,
  agentExecution: (id: string) => ['agent-execution', id] as const,
  // Keys for real-time status polling
  executionStatus: (id: string) => ['execution-status', id] as const,
  workflowStatus: (id: string) => ['workflow-status', id] as const,
  statusUpdate: (id: string) => ['status-update', id] as const,
}

// Health check hook
export function useHealthCheck() {
  return useQuery({
    queryKey: queryKeys.health,
    queryFn: async (): Promise<HealthCheck> => {
      const response = await api.get('/api/v1/health/')
      return validateSchema(HealthCheckSchema, response.data)
    },
    staleTime: 30000, // 30 seconds
    gcTime: 60000, // 1 minute
  })
}

// File upload hooks
export function useFileUpload() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (file: File): Promise<FileUploadResponse> => {
      const formData = new FormData()
      formData.append('file', file)
      
      const response = await api.post('/files/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      
      return validateSchema(FileUploadResponseSchema, response.data)
    },
    onSuccess: () => {
      // Invalidate files list to refetch
      queryClient.invalidateQueries({ queryKey: queryKeys.files })
    },
  })
}

// Data preview hooks
export function useDataPreview(fileId: string, page: number = 1, enabled: boolean = true) {
  return useQuery({
    queryKey: queryKeys.dataPreview(fileId, page),
    queryFn: async (): Promise<DataPreview> => {
      const response = await api.get(`/data/preview/${fileId}`, {
        params: { page, pageSize: 20 }
      })
      return validateSchema(DataPreviewSchema, response.data)
    },
    enabled: enabled && !!fileId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

// Workflow hooks
export function useWorkflows() {
  return useQuery({
    queryKey: queryKeys.workflows,
    queryFn: async (): Promise<WorkflowStatus[]> => {
      const response = await api.get('/workflows')
      return response.data.map((workflow: unknown) => 
        validateSchema(WorkflowStatusSchema, workflow)
      )
    },
    refetchInterval: 2000, // Poll every 2 seconds for real-time updates
  })
}

export function useWorkflow(id: string, enabled: boolean = true) {
  return useQuery({
    queryKey: queryKeys.workflow(id),
    queryFn: async (): Promise<WorkflowStatus> => {
      const response = await api.get(`/workflows/${id}`)
      return validateSchema(WorkflowStatusSchema, response.data)
    },
    enabled: enabled && !!id,
    refetchInterval: 1000, // Poll every second for real-time updates
  })
}

// Query execution hooks
export function useExecuteQuery() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (queryRequest: QueryRequest): Promise<QueryResponse> => {
      const response = await api.post('/queries/execute', queryRequest)
      return validateSchema(QueryResponseSchema, response.data)
    },
    onSuccess: (data) => {
      // Cache the query result
      queryClient.setQueryData(queryKeys.query(data.id), data)
      // Invalidate queries list
      queryClient.invalidateQueries({ queryKey: queryKeys.queries })
    },
  })
}

export function useQuery_custom(id: string, enabled: boolean = true) {
  return useQuery({
    queryKey: queryKeys.query(id),
    queryFn: async (): Promise<QueryResponse> => {
      const response = await api.get(`/queries/${id}`)
      return validateSchema(QueryResponseSchema, response.data)
    },
    enabled: enabled && !!id,
  })
}

// File management hooks
export function useFiles() {
  return useQuery({
    queryKey: queryKeys.files,
    queryFn: async () => {
      const response = await api.get('/files')
      return response.data
    },
  })
}

export function useDeleteFile() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (fileId: string) => {
      await api.delete(`/files/${fileId}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.files })
    },
  })
}

// Prefetch helpers
export function usePrefetchDataPreview() {
  const queryClient = useQueryClient()
  
  return (fileId: string, page: number = 1) => {
    queryClient.prefetchQuery({
      queryKey: queryKeys.dataPreview(fileId, page),
      queryFn: async (): Promise<DataPreview> => {
        const response = await api.get(`/data/preview/${fileId}`, {
          params: { page, pageSize: 20 }
        })
        return validateSchema(DataPreviewSchema, response.data)
      },
      staleTime: 5 * 60 * 1000,
    })
  }
}

// Error handling hook
export function useErrorHandler() {
  return (error: any) => {
    console.error('API Error:', error)
    
    // You can add global error handling here
    // e.g., show notifications, redirect on auth errors, etc.
    
    if (error?.response?.status === 401) {
      // Handle unauthorized
      console.warn('User needs to re-authenticate')
    }
    
    if (error?.response?.status >= 500) {
      // Handle server errors
      console.error('Server error occurred')
    }
  }
}

// Agent execution hooks
export function useExecuteAgent() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (request: AgentExecutionRequest): Promise<AgentExecutionResponse> => {
      const response = await api.post('/api/v1/agents/execute', request)
      return response.data
    },
    onSuccess: (data) => {
      // Cache the execution
      queryClient.setQueryData(queryKeys.agentExecution(data.execution_id), data)
    },
  })
}

export function useAgentExecutionStatus(executionId: string, enabled: boolean = true) {
  return useQuery({
    queryKey: queryKeys.agentExecution(executionId),
    queryFn: async () => {
      const response = await api.get(`/api/v1/agents/execution/${executionId}`)
      return response.data
    },
    enabled: enabled && !!executionId,
    refetchInterval: 2000, // Poll every 2 seconds for status updates
  })
}

// Session management hooks
export function useCreateSession() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (request: SessionRequest): Promise<Session> => {
      const response = await api.post('/api/v1/agents/session', request)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.sessions })
    },
  })
}

export function useSession(sessionId: string, enabled: boolean = true) {
  return useQuery({
    queryKey: queryKeys.session(sessionId),
    queryFn: async (): Promise<Session> => {
      const response = await api.get(`/api/v1/agents/session/${sessionId}`)
      return response.data
    },
    enabled: enabled && !!sessionId,
  })
}

export function useSessions() {
  return useQuery({
    queryKey: queryKeys.sessions,
    queryFn: async (): Promise<Session[]> => {
      const response = await api.get('/api/v1/agents/sessions')
      return response.data
    },
  })
}

// Conversation hooks
export function useSendMessage() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (request: ConversationRequest): Promise<ConversationMessage> => {
      const response = await api.post('/api/v1/agents/conversation', request)
      return response.data
    },
    onSuccess: (_, variables) => {
      // Invalidate conversation history for this session
      queryClient.invalidateQueries({ 
        queryKey: queryKeys.conversation(variables.session_id) 
      })
    },
  })
}

export function useConversationHistory(sessionId: string, enabled: boolean = true) {
  return useQuery({
    queryKey: queryKeys.conversation(sessionId),
    queryFn: async (): Promise<ConversationMessage[]> => {
      const response = await api.get(`/api/v1/agents/conversation/${sessionId}/history`)
      return response.data
    },
    enabled: enabled && !!sessionId,
    refetchInterval: 3000, // Poll every 3 seconds for new messages
  })
}

// Real-time status tracking hooks
export function useExecutionStatus(executionId: string, enabled: boolean = true) {
  return useQuery({
    queryKey: queryKeys.executionStatus(executionId),
    queryFn: async (): Promise<ExecutionStatus> => {
      const response = await api.get(`/api/v1/agents/execution/${executionId}`)
      return response.data
    },
    enabled: enabled && !!executionId,
    refetchInterval: (query) => {
      // Stop polling if execution is completed or failed
      if (query.state.data?.status === 'completed' || query.state.data?.status === 'failed') {
        return false
      }
      // Poll every 1 second for active executions
      return 1000
    },
    staleTime: 0, // Always refetch to get latest status
  })
}

export function useWorkflowStatus(workflowId: string, enabled: boolean = true) {
  return useQuery({
    queryKey: queryKeys.workflowStatus(workflowId),
    queryFn: async (): Promise<WorkflowStatus> => {
      const response = await api.get(`/api/v1/agents/workflow/${workflowId}`)
      return response.data
    },
    enabled: enabled && !!workflowId,
    refetchInterval: (query) => {
      // Stop polling if workflow is completed or failed
      if (query.state.data?.status === 'completed' || query.state.data?.status === 'failed') {
        return false
      }
      // Poll every 1 second for active workflows
      return 1000
    },
    staleTime: 0, // Always refetch to get latest status
  })
}

export function useStatusUpdate(sessionId: string, enabled: boolean = true) {
  return useQuery({
    queryKey: queryKeys.statusUpdate(sessionId),
    queryFn: async (): Promise<StatusUpdate[]> => {
      const response = await api.get(`/api/v1/agents/status/${sessionId}`)
      return response.data
    },
    enabled: enabled && !!sessionId,
    refetchInterval: 2000, // Poll every 2 seconds for status updates
    staleTime: 0, // Always refetch to get latest updates
  })
}

// Enhanced agent execution hook with real-time status tracking
export function useAgentExecutionWithStatus() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (request: AgentExecutionRequest): Promise<AgentExecutionResponse> => {
      const response = await api.post('/api/v1/agents/execute', request)
      return response.data
    },
    onSuccess: (data) => {
      // Invalidate and immediately start polling for execution status
      queryClient.invalidateQueries({ 
        queryKey: queryKeys.executionStatus(data.execution_id) 
      })
      
      // Start polling for the execution status
      queryClient.prefetchQuery({
        queryKey: queryKeys.executionStatus(data.execution_id),
        queryFn: async () => {
          const response = await api.get(`/api/v1/agents/execution/${data.execution_id}`)
          return response.data
        },
      })
    },
  })
}

// Enhanced workflow execution hook with real-time status tracking
export function useWorkflowExecutionWithStatus() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (request: any): Promise<any> => {
      const response = await api.post('/api/v1/agents/workflow/execute', request)
      return response.data
    },
    onSuccess: (data) => {
      // Invalidate and immediately start polling for workflow status
      queryClient.invalidateQueries({ 
        queryKey: queryKeys.workflowStatus(data.workflow_id) 
      })
      
      // Start polling for the workflow status
      queryClient.prefetchQuery({
        queryKey: queryKeys.workflowStatus(data.workflow_id),
        queryFn: async () => {
          const response = await api.get(`/api/v1/agents/workflow/${data.workflow_id}`)
          return response.data
        },
      })
    },
  })
}
