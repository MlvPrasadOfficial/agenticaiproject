'use client';

import React, { useState, useCallback } from 'react';
import { v4 as uuidv4 } from 'uuid';
import FileUpload, { UploadedFile } from './file-upload';
import { useFileUpload } from '@/hooks/api';
import { Play, Pause, RotateCcw, Trash2, CheckCircle2, AlertTriangle } from 'lucide-react';

interface FileUploadQueueProps {
  onUploadComplete?: (files: UploadedFile[]) => void;
  onUploadError?: (error: string) => void;
  className?: string;
}

const FileUploadQueue: React.FC<FileUploadQueueProps> = ({
  onUploadComplete,
  onUploadError,
  className = ''
}) => {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  
  const uploadMutation = useFileUpload();

  const handleFilesSelected = useCallback((newFiles: File[]) => {
    const uploadFiles: UploadedFile[] = newFiles.map(file => ({
      id: uuidv4(),
      file,
      status: 'pending' as const,
      progress: 0
    }));
    
    setFiles(prevFiles => [...prevFiles, ...uploadFiles]);
  }, []);

  const handleFileRemove = useCallback((fileId: string) => {
    setFiles(prevFiles => prevFiles.filter(file => file.id !== fileId));
  }, []);

  const updateFileStatus = useCallback((fileId: string, updates: Partial<UploadedFile>) => {
    setFiles(prevFiles => 
      prevFiles.map(file => 
        file.id === fileId ? { ...file, ...updates } : file
      )
    );
  }, []);

  const processUploadQueue = useCallback(async () => {
    if (isProcessing || isPaused) return;
    
    setIsProcessing(true);
    const pendingFiles = files.filter(file => file.status === 'pending');
    
    for (const file of pendingFiles) {
      if (isPaused) break;
      
      try {
        updateFileStatus(file.id, { status: 'uploading', progress: 0 });
        
        // Simulate progress updates
        const progressInterval = setInterval(() => {
          updateFileStatus(file.id, { 
            progress: Math.min(file.progress + Math.random() * 30, 90) 
          });
        }, 500);
        
        // Use the actual upload mutation
        const result = await uploadMutation.mutateAsync(file.file);
        
        clearInterval(progressInterval);
        updateFileStatus(file.id, { 
          status: 'success', 
          progress: 100 
        });
        
      } catch (error) {
        updateFileStatus(file.id, { 
          status: 'error', 
          progress: 0,
          error: error instanceof Error ? error.message : 'Upload failed'
        });
        
        if (onUploadError) {
          onUploadError(error instanceof Error ? error.message : 'Upload failed');
        }
      }
    }
    
    setIsProcessing(false);
    
    // Check if all uploads completed successfully
    const completedFiles = files.filter(file => file.status === 'success');
    if (completedFiles.length > 0 && onUploadComplete) {
      onUploadComplete(completedFiles);
    }
  }, [files, isProcessing, isPaused, uploadMutation, updateFileStatus, onUploadComplete, onUploadError]);

  const handleStartQueue = useCallback(() => {
    setIsPaused(false);
    processUploadQueue();
  }, [processUploadQueue]);

  const handlePauseQueue = useCallback(() => {
    setIsPaused(true);
  }, []);

  const handleRetryFailed = useCallback(() => {
    setFiles(prevFiles => 
      prevFiles.map(file => 
        file.status === 'error' 
          ? { ...file, status: 'pending' as const, progress: 0, error: undefined }
          : file
      )
    );
  }, []);

  const handleClearCompleted = useCallback(() => {
    setFiles(prevFiles => 
      prevFiles.filter(file => file.status !== 'success')
    );
  }, []);

  const handleClearAll = useCallback(() => {
    if (isProcessing) {
      setIsPaused(true);
    }
    setFiles([]);
    setIsProcessing(false);
    setIsPaused(false);
  }, [isProcessing]);

  const getQueueStats = useCallback(() => {
    const total = files.length;
    const pending = files.filter(f => f.status === 'pending').length;
    const uploading = files.filter(f => f.status === 'uploading').length;
    const success = files.filter(f => f.status === 'success').length;
    const error = files.filter(f => f.status === 'error').length;
    
    return { total, pending, uploading, success, error };
  }, [files]);

  const stats = getQueueStats();
  const hasPendingFiles = stats.pending > 0;
  const hasErrorFiles = stats.error > 0;
  const hasCompletedFiles = stats.success > 0;

  return (
    <div className={`w-full space-y-6 ${className}`}>
      {/* File Upload Component */}
      <FileUpload
        onFilesSelected={handleFilesSelected}
        onFileRemove={handleFileRemove}
        uploadedFiles={files}
        multiple={true}
        maxFiles={20}
      />

      {/* Queue Controls */}
      {files.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
          {/* Queue Stats */}
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-6 text-sm">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-gray-400 rounded-full"></div>
                <span className="text-gray-600 dark:text-gray-400">
                  Pending: {stats.pending}
                </span>
              </div>
              
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                <span className="text-gray-600 dark:text-gray-400">
                  Uploading: {stats.uploading}
                </span>
              </div>
              
              <div className="flex items-center space-x-2">
                <CheckCircle2 className="w-3 h-3 text-green-500" />
                <span className="text-gray-600 dark:text-gray-400">
                  Completed: {stats.success}
                </span>
              </div>
              
              {hasErrorFiles && (
                <div className="flex items-center space-x-2">
                  <AlertTriangle className="w-3 h-3 text-red-500" />
                  <span className="text-gray-600 dark:text-gray-400">
                    Failed: {stats.error}
                  </span>
                </div>
              )}
            </div>
            
            <div className="text-sm font-medium text-gray-900 dark:text-gray-100">
              Total: {stats.total}
            </div>
          </div>

          {/* Control Buttons */}
          <div className="flex items-center space-x-3">
            {!isProcessing && hasPendingFiles && (
              <button
                onClick={handleStartQueue}
                disabled={uploadMutation.isPending}
                className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
              >
                <Play className="w-4 h-4" />
                <span>Start Upload</span>
              </button>
            )}

            {isProcessing && !isPaused && (
              <button
                onClick={handlePauseQueue}
                className="flex items-center space-x-2 px-4 py-2 bg-orange-600 hover:bg-orange-700 text-white rounded-lg transition-colors"
              >
                <Pause className="w-4 h-4" />
                <span>Pause</span>
              </button>
            )}

            {isPaused && (
              <button
                onClick={handleStartQueue}
                className="flex items-center space-x-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors"
              >
                <Play className="w-4 h-4" />
                <span>Resume</span>
              </button>
            )}

            {hasErrorFiles && (
              <button
                onClick={handleRetryFailed}
                className="flex items-center space-x-2 px-4 py-2 bg-yellow-600 hover:bg-yellow-700 text-white rounded-lg transition-colors"
              >
                <RotateCcw className="w-4 h-4" />
                <span>Retry Failed</span>
              </button>
            )}

            {hasCompletedFiles && (
              <button
                onClick={handleClearCompleted}
                className="flex items-center space-x-2 px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors"
              >
                <CheckCircle2 className="w-4 h-4" />
                <span>Clear Completed</span>
              </button>
            )}

            <button
              onClick={handleClearAll}
              className="flex items-center space-x-2 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
            >
              <Trash2 className="w-4 h-4" />
              <span>Clear All</span>
            </button>
          </div>

          {/* Processing Status */}
          {isProcessing && (
            <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-950/20 rounded-lg">
              <div className="flex items-center space-x-2">
                <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
                <span className="text-sm text-blue-800 dark:text-blue-200">
                  {isPaused ? 'Upload paused...' : 'Processing upload queue...'}
                </span>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default FileUploadQueue;
