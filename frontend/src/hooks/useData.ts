/**
 * Custom React hooks for data management and API integration
 */

import { useState, useCallback, useEffect } from 'react';
import {
  uploadFile,
  getDataPreview,
  getDataStatistics,
  deleteFile,
  checkBackendConnection,
  FileUploadResponse,
  DataPreviewResponse,
  DataStatisticsResponse,
  ApiException,
} from '../services/api';

// Upload state management
export interface UploadState {
  isUploading: boolean;
  progress: number;
  error: string | null;
  uploadedFile: FileUploadResponse | null;
}

export function useFileUpload() {
  const [uploadState, setUploadState] = useState<UploadState>({
    isUploading: false,
    progress: 0,
    error: null,
    uploadedFile: null,
  });

  const upload = useCallback(async (file: File) => {
    setUploadState({
      isUploading: true,
      progress: 0,
      error: null,
      uploadedFile: null,
    });

    try {
      const result = await uploadFile(file, (progress) => {
        setUploadState(prev => ({ ...prev, progress }));
      });

      setUploadState({
        isUploading: false,
        progress: 100,
        error: null,
        uploadedFile: result,
      });

      return result;
    } catch (error) {
      const errorMessage = error instanceof ApiException 
        ? error.detail 
        : 'Upload failed. Please try again.';
      
      setUploadState({
        isUploading: false,
        progress: 0,
        error: errorMessage,
        uploadedFile: null,
      });
      
      throw error;
    }
  }, []);

  const reset = useCallback(() => {
    setUploadState({
      isUploading: false,
      progress: 0,
      error: null,
      uploadedFile: null,
    });
  }, []);

  const removeFile = useCallback(async () => {
    if (uploadState.uploadedFile) {
      try {
        await deleteFile(uploadState.uploadedFile.file_id);
      } catch (error) {
        console.warn('Failed to delete file from server:', error);
      }
    }
    reset();
  }, [uploadState.uploadedFile, reset]);

  return {
    ...uploadState,
    upload,
    reset,
    removeFile,
  };
}

// Data preview state management
export interface DataPreviewState {
  isLoading: boolean;
  error: string | null;
  preview: DataPreviewResponse | null;
  statistics: DataStatisticsResponse | null;
}

export function useDataPreview(fileId: string | null) {
  const [state, setState] = useState<DataPreviewState>({
    isLoading: false,
    error: null,
    preview: null,
    statistics: null,
  });

  const loadPreview = useCallback(async (rows: number = 10) => {
    if (!fileId) return;

    setState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      const [preview, statistics] = await Promise.all([
        getDataPreview(fileId, rows),
        getDataStatistics(fileId),
      ]);

      setState({
        isLoading: false,
        error: null,
        preview,
        statistics,
      });
    } catch (error) {
      const errorMessage = error instanceof ApiException 
        ? error.detail 
        : 'Failed to load data preview';
      
      setState({
        isLoading: false,
        error: errorMessage,
        preview: null,
        statistics: null,
      });
    }
  }, [fileId]);

  const reset = useCallback(() => {
    setState({
      isLoading: false,
      error: null,
      preview: null,
      statistics: null,
    });
  }, []);

  // Auto-load preview when fileId changes
  useEffect(() => {
    if (fileId) {
      loadPreview();
    } else {
      reset();
    }
  }, [fileId, loadPreview, reset]);

  return {
    ...state,
    loadPreview,
    reset,
  };
}

// Backend connection status
export function useBackendConnection() {
  const [isConnected, setIsConnected] = useState<boolean | null>(null);
  const [isChecking, setIsChecking] = useState(false);

  const checkConnection = useCallback(async () => {
    setIsChecking(true);
    try {
      const connected = await checkBackendConnection();
      setIsConnected(connected);
    } catch {
      setIsConnected(false);
    } finally {
      setIsChecking(false);
    }
  }, []);

  // Check connection on mount and periodically
  useEffect(() => {
    checkConnection();
    
    const interval = setInterval(checkConnection, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, [checkConnection]);

  return {
    isConnected,
    isChecking,
    checkConnection,
  };
}

// Query/chat state management (placeholder for future implementation)
export interface ChatMessage {
  id: string;
  type: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  metadata?: Record<string, any>;
}

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);

  const sendMessage = useCallback(async (content: string) => {
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsProcessing(true);

    try {
      // TODO: Implement actual chat API call
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate processing
      
      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: `I understand you're asking: "${content}". This feature is coming soon!`,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'system',
        content: 'Sorry, I encountered an error processing your request.',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsProcessing(false);
    }
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  return {
    messages,
    isProcessing,
    sendMessage,
    clearMessages,
  };
}
