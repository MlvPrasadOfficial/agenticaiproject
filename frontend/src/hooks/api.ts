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
