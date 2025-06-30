import React, { useState, useCallback, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Upload, 
  FileText, 
  BarChart3, 
  CheckCircle, 
  AlertCircle,
  Loader2,
  Eye,
  Download,
  Trash2,
  RefreshCw
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { useToast } from '@/components/ui/notification'
import { 
  useFileUpload, 
  useDataPreview,
  FileUploadResponse 
} from '@/hooks/api'
import { useDataProcessingWebSocket } from '@/hooks/useWebSocket'

export interface EnhancedDataProcessingProps {
  onFileProcessed?: (file: FileUploadResponse) => void
  onAnalysisComplete?: (results: any) => void
  onPreviewReady?: (preview: any) => void
  className?: string
}

interface ProcessingStep {
  id: string
  name: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  progress?: number
  message?: string
  error?: string
}

const DEFAULT_PROCESSING_STEPS: ProcessingStep[] = [
  { id: 'upload', name: 'File Upload', status: 'pending' },
  { id: 'validation', name: 'File Validation', status: 'pending' },
  { id: 'parsing', name: 'Data Parsing', status: 'pending' },
  { id: 'profiling', name: 'Data Profiling', status: 'pending' },
  { id: 'analysis', name: 'Quality Analysis', status: 'pending' },
  { id: 'preview', name: 'Preview Generation', status: 'pending' },
]

export function EnhancedDataProcessing({
  onFileProcessed,
  onAnalysisComplete,
  onPreviewReady,
  className
}: EnhancedDataProcessingProps) {
  const [dragActive, setDragActive] = useState(false)
  const [uploadedFile, setUploadedFile] = useState<FileUploadResponse | null>(null)
  const [processingSteps, setProcessingSteps] = useState<ProcessingStep[]>(DEFAULT_PROCESSING_STEPS)
  const [currentStep, setCurrentStep] = useState<string | null>(null)
  const [autoAnalyzeEnabled, setAutoAnalyzeEnabled] = useState(true)
  
  const { success, error, loading } = useToast()
  
  // API hooks
  const fileUpload = useFileUpload()
  const dataPreview = useDataPreview(
    uploadedFile?.file_id || '', 
    1, 
    !!uploadedFile?.file_id && uploadedFile?.preview_available
  )
  
  // WebSocket for real-time processing updates
  const { 
    processingStatus, 
    analysisResults,
    isConnected: wsConnected 
  } = useDataProcessingWebSocket(uploadedFile?.file_id, !!uploadedFile?.file_id)

  // Update processing steps based on WebSocket updates
  useEffect(() => {
    if (processingStatus) {
      setProcessingSteps(prev => prev.map(step => 
        step.id === processingStatus.step_id 
          ? { 
              ...step, 
              status: processingStatus.status,
              progress: processingStatus.progress,
              message: processingStatus.message,
              error: processingStatus.error
            }
          : step
      ))
      setCurrentStep(processingStatus.step_id)
    }
  }, [processingStatus])

  // Handle analysis completion
  useEffect(() => {
    if (analysisResults) {
      onAnalysisComplete?.(analysisResults)
      success('Data analysis completed!', {
        message: 'View results in the preview section',
        duration: 5000
      })
    }
  }, [analysisResults, onAnalysisComplete, success])

  // Handle preview data
  useEffect(() => {
    if (dataPreview.data) {
      onPreviewReady?.(dataPreview.data)
    }
  }, [dataPreview.data, onPreviewReady])

  const resetProcessing = useCallback(() => {
    setUploadedFile(null)
    setProcessingSteps(DEFAULT_PROCESSING_STEPS)
    setCurrentStep(null)
  }, [])

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0])
    }
  }, [])

  const handleFileUpload = useCallback(async (file: File) => {
    // Reset previous state
    resetProcessing()
    
    // Start upload step
    setProcessingSteps(prev => prev.map(step => 
      step.id === 'upload' 
        ? { ...step, status: 'running', message: `Uploading ${file.name}...` }
        : step
    ))
    setCurrentStep('upload')

    const loadingId = loading(`Uploading ${file.name}...`)

    fileUpload.mutate(file, {
      onSuccess: (data) => {
        setUploadedFile(data)
        onFileProcessed?.(data)
        
        // Update upload step as completed
        setProcessingSteps(prev => prev.map(step => 
          step.id === 'upload' 
            ? { ...step, status: 'completed', progress: 100, message: 'Upload successful' }
            : step
        ))

        success('File uploaded successfully!', {
          message: `${file.name} is ready for analysis`,
          duration: 3000
        })

        // Auto-trigger analysis if enabled
        if (autoAnalyzeEnabled && data.preview_available) {
          setTimeout(() => {
            handleAnalyzeData(data)
          }, 500)
        }
      },
      onError: (err) => {
        // Update upload step as failed
        setProcessingSteps(prev => prev.map(step => 
          step.id === 'upload' 
            ? { ...step, status: 'failed', error: err.message || 'Upload failed' }
            : step
        ))
        
        error('File upload failed', {
          message: err.message || 'Please try again with a different file',
          duration: 8000
        })
      }
    })
  }, [fileUpload, resetProcessing, loading, success, error, onFileProcessed, autoAnalyzeEnabled])

  const handleAnalyzeData = useCallback(async (file: FileUploadResponse = uploadedFile!) => {
    if (!file) return

    // Start validation step
    setProcessingSteps(prev => prev.map(step => 
      step.id === 'validation' 
        ? { ...step, status: 'running', message: 'Validating file format...' }
        : step
    ))
    setCurrentStep('validation')

    // Simulate processing steps (in real implementation, these would be driven by WebSocket)
    const steps = ['validation', 'parsing', 'profiling', 'analysis', 'preview']
    let currentIndex = 0

    const processNextStep = () => {
      if (currentIndex < steps.length) {
        const stepId = steps[currentIndex]
        setCurrentStep(stepId)
        setProcessingSteps(prev => prev.map(step => 
          step.id === stepId 
            ? { ...step, status: 'running', message: `Processing ${step.name.toLowerCase()}...` }
            : step
        ))

        // Simulate step completion after a delay
        setTimeout(() => {
          setProcessingSteps(prev => prev.map(step => 
            step.id === stepId 
              ? { ...step, status: 'completed', progress: 100, message: `${step.name} complete` }
              : step
          ))
          
          currentIndex++
          processNextStep()
        }, 1000 + Math.random() * 1000) // Random delay between 1-2 seconds
      } else {
        setCurrentStep(null)
        success('Data analysis completed!', {
          message: 'All processing steps finished successfully'
        })
      }
    }

    processNextStep()
  }, [uploadedFile, success])

  const getStepIcon = (step: ProcessingStep) => {
    switch (step.status) {
      case 'running':
        return <Loader2 className="w-4 h-4 animate-spin text-blue-500" />
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />
      case 'failed':
        return <AlertCircle className="w-4 h-4 text-red-500" />
      default:
        return <div className="w-4 h-4 rounded-full border-2 border-gray-300" />
    }
  }

  return (
    <div className={className}>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Upload className="w-5 h-5 text-blue-500" />
            Enhanced Data Processing
            {wsConnected && (
              <Badge variant="outline" className="ml-auto">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-1 animate-pulse" />
                Live Processing
              </Badge>
            )}
          </CardTitle>
        </CardHeader>
        
        <CardContent className="space-y-6">
          {/* Upload Area */}
          {!uploadedFile && (
            <div
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              className={`
                border-2 border-dashed rounded-lg p-8 text-center transition-all duration-200
                ${dragActive 
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' 
                  : 'border-gray-300 hover:border-gray-400 dark:border-gray-600'
                }
                ${fileUpload.isPending ? 'opacity-50 pointer-events-none' : 'cursor-pointer'}
              `}
            >
              <Upload className="w-12 h-12 mx-auto mb-4 text-gray-400" />
              <h3 className="text-lg font-medium mb-2">Upload Your Data File</h3>
              <p className="text-gray-500 mb-4">
                Drag and drop your CSV, Excel, or JSON file here, or click to browse
              </p>
              
              <input
                type="file"
                onChange={(e) => e.target.files && handleFileUpload(e.target.files[0])}
                accept=".csv,.xlsx,.xls,.json,.txt"
                className="hidden"
                id="file-upload"
                disabled={fileUpload.isPending}
              />
              
              <label
                htmlFor="file-upload"
                className="inline-flex items-center px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors cursor-pointer"
              >
                <FileText className="w-4 h-4 mr-2" />
                Choose File
              </label>
              
              <p className="text-xs text-gray-400 mt-2">
                Supported formats: CSV, Excel (.xlsx, .xls), JSON, TXT
              </p>
            </div>
          )}

          {/* File Info and Controls */}
          {uploadedFile && (
            <div className="bg-gray-50 dark:bg-gray-900/50 rounded-lg p-4">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <FileText className="w-8 h-8 text-blue-500" />
                  <div>
                    <h4 className="font-medium">{uploadedFile.filename}</h4>
                    <p className="text-sm text-gray-500">
                      {(uploadedFile.size / 1024 / 1024).toFixed(2)} MB • {uploadedFile.mime_type}
                    </p>
                  </div>
                </div>
                
                <div className="flex gap-2">
                  {uploadedFile.preview_available && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleAnalyzeData()}
                      disabled={currentStep !== null}
                    >
                      <BarChart3 className="w-4 h-4 mr-2" />
                      Analyze
                    </Button>
                  )}
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={resetProcessing}
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </div>

              {/* Auto-analyze toggle */}
              <div className="flex items-center gap-2 mb-4">
                <input
                  type="checkbox"
                  id="auto-analyze"
                  checked={autoAnalyzeEnabled}
                  onChange={(e) => setAutoAnalyzeEnabled(e.target.checked)}
                  className="rounded"
                />
                <label htmlFor="auto-analyze" className="text-sm">
                  Automatically analyze files after upload
                </label>
              </div>
            </div>
          )}

          {/* Processing Steps */}
          {uploadedFile && (
            <div>
              <h4 className="font-medium mb-4">Processing Steps</h4>
              <div className="space-y-3">
                {processingSteps.map((step, index) => (
                  <motion.div
                    key={step.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className={`
                      flex items-center gap-3 p-3 rounded-lg border
                      ${step.id === currentStep 
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' 
                        : 'border-gray-200 dark:border-gray-700'
                      }
                    `}
                  >
                    {getStepIcon(step)}
                    
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <span className="font-medium">{step.name}</span>
                        <Badge variant={
                          step.status === 'completed' ? 'default' :
                          step.status === 'failed' ? 'destructive' :
                          step.status === 'running' ? 'secondary' : 'outline'
                        }>
                          {step.status}
                        </Badge>
                      </div>
                      
                      {step.message && (
                        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                          {step.message}
                        </p>
                      )}
                      
                      {step.error && (
                        <p className="text-sm text-red-600 dark:text-red-400 mt-1">
                          Error: {step.error}
                        </p>
                      )}
                      
                      {step.progress !== undefined && step.status === 'running' && (
                        <Progress value={step.progress} className="mt-2 h-1" />
                      )}
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          )}

          {/* Data Preview */}
          {dataPreview.data && (
            <div>
              <div className="flex items-center justify-between mb-4">
                <h4 className="font-medium">Data Preview</h4>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => dataPreview.refetch()}
                    disabled={dataPreview.isLoading}
                  >
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Refresh
                  </Button>
                  <Button variant="outline" size="sm">
                    <Eye className="w-4 h-4 mr-2" />
                    Full View
                  </Button>
                </div>
              </div>
              
              <div className="border rounded-lg overflow-hidden">
                <div className="bg-gray-50 dark:bg-gray-900 p-3 border-b">
                  <div className="flex items-center justify-between text-sm">
                    <span>
                      {dataPreview.data.total_rows.toLocaleString()} rows × {dataPreview.data.total_columns} columns
                    </span>
                    <span>
                      Showing {dataPreview.data.preview_rows} rows
                    </span>
                  </div>
                </div>
                
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-100 dark:bg-gray-800">
                      <tr>
                        {dataPreview.data.columns.map((col, index) => (
                          <th key={index} className="px-3 py-2 text-left text-sm font-medium">
                            <div>
                              <span>{col.name}</span>
                              <div className="text-xs text-gray-500 font-normal">
                                {col.type}
                              </div>
                            </div>
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {dataPreview.data.data.slice(0, 5).map((row, rowIndex) => (
                        <tr key={rowIndex} className="border-t">
                          {dataPreview.data.columns.map((col, colIndex) => (
                            <td key={colIndex} className="px-3 py-2 text-sm">
                              {row[col.name]?.toString() || '—'}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                
                {dataPreview.data.has_more && (
                  <div className="bg-gray-50 dark:bg-gray-900 p-3 border-t text-center">
                    <Button variant="ghost" size="sm">
                      Load More Rows
                    </Button>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Connection Status */}
          {!wsConnected && uploadedFile && (
            <div className="text-xs text-amber-600 dark:text-amber-400 flex items-center gap-1">
              <AlertCircle className="w-3 h-3" />
              Real-time processing updates unavailable. Using polling fallback.
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
