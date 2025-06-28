'use client';

import { useState, useRef } from "react";
import { Upload, Send, File, X, AlertCircle, CheckCircle } from "lucide-react";
import AgentList from "./AgentList";
import DataPreview from "./DataPreview";
import { HealthIndicator } from "./ui/health-indicator";
import { useFileUpload, useDataPreview, useBackendConnection, useChat } from "../hooks/useData";

interface UploadedFile {
  name: string;
  size: number;
  type: string;
}

export default function Dashboard() {
  const [input, setInput] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [showDataPreview, setShowDataPreview] = useState(false);

  // Custom hooks for API integration
  const { 
    isUploading, 
    progress, 
    error: uploadError, 
    uploadedFile, 
    upload, 
    removeFile 
  } = useFileUpload();
  
  const { 
    isLoading: previewLoading, 
    error: previewError, 
    preview, 
    statistics 
  } = useDataPreview(uploadedFile?.file_id || null);
  
  const { isConnected, isChecking } = useBackendConnection();
  const { messages, isProcessing, sendMessage } = useChat();

  const handleFileUpload = async (file: File) => {
    try {
      await upload(file);
      setShowDataPreview(true);
    } catch (error) {
      console.error('Upload failed:', error);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFileUpload(files[0]);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileUpload(files[0]);
    }
  };

  const removeFileHandler = async () => {
    await removeFile();
    setShowDataPreview(false);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const handleSendQuery = async () => {
    if (input.trim()) {
      await sendMessage(input);
      setInput('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendQuery();
    }
  };

  return (
    <div className="min-h-screen bg-dark-primary">
      {/* System Health Status */}
      <div className="fixed top-4 right-4 z-50">
        <div className="px-3 py-2 rounded-full bg-glass-bg border border-glass-border backdrop-blur-sm">
          <HealthIndicator />
        </div>
      </div>

      {!showDataPreview ? (
        /* Main Dashboard View */
        <div className="flex flex-row justify-center min-h-screen items-center gap-8 p-6 animate-fade-in">
      {/* Left Side */}
      <div className="flex flex-col gap-8 w-[400px]">
        {/* Upload Data Card */}
        <div className="card-glass p-6 animate-slide-in">
          <h2 className="text-2xl font-bold text-text-primary mb-6 flex items-center gap-3">
            <Upload className="w-6 h-6 text-accent-primary" />
            Upload your Data
          </h2>
          
          {!uploadedFile ? (
            <div>
              <div
                className={`border-2 border-dashed rounded-xl p-8 text-center transition-all duration-300 cursor-pointer ${
                  isDragOver 
                    ? 'border-accent-primary bg-accent-primary/10 text-accent-primary' 
                    : 'border-glass-border bg-glass-bg hover:border-accent-primary/50 hover:bg-glass-hover text-text-secondary'
                }`}
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onClick={() => !isUploading && fileInputRef.current?.click()}
              >
                <Upload className={`w-12 h-12 mx-auto mb-4 ${isDragOver ? 'text-accent-primary' : 'text-text-muted'}`} />
                <p className="text-lg font-medium mb-2">
                  {isDragOver ? 'Drop your file here' : 'Drag and drop a file here'}
                </p>
                <p className="text-sm text-text-muted">
                  or click to browse
                </p>
                <input
                  ref={fileInputRef}
                  type="file"
                  className="hidden"
                  accept=".csv,.xlsx,.xls,.json"
                  onChange={handleFileInputChange}
                  disabled={isUploading}
                />
              </div>

              {/* Upload Progress */}
              {isUploading && (
                <div className="mt-4">
                  <div className="flex items-center justify-between text-sm mb-2">
                    <span className="text-text-secondary">Uploading...</span>
                    <span className="text-accent-primary">{Math.round(progress)}%</span>
                  </div>
                  <div className="w-full bg-dark-tertiary rounded-full h-2">
                    <div 
                      className="bg-gradient-to-r from-accent-primary to-accent-secondary h-2 rounded-full transition-all duration-300"
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                </div>
              )}

              {/* Upload Error */}
              {uploadError && (
                <div className="mt-4 p-3 bg-accent-error/10 border border-accent-error/20 rounded-lg flex items-start gap-2">
                  <AlertCircle className="w-4 h-4 text-accent-error mt-0.5 flex-shrink-0" />
                  <div>
                    <p className="text-sm font-medium text-accent-error">Upload Failed</p>
                    <p className="text-xs text-text-secondary mt-1">{uploadError}</p>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="space-y-4">
              <div className="bg-glass-bg border border-glass-border rounded-xl p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <File className="w-8 h-8 text-accent-tertiary" />
                    <div>
                      <p className="font-medium text-text-primary">{uploadedFile.filename}</p>
                      <p className="text-sm text-text-muted">{formatFileSize(uploadedFile.size)}</p>
                      {uploadedFile.validation_results.warnings.length > 0 && (
                        <p className="text-xs text-yellow-400 mt-1">
                          {uploadedFile.validation_results.warnings.length} warning(s)
                        </p>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {uploadedFile.status === 'success' && (
                      <CheckCircle className="w-5 h-5 text-accent-tertiary" />
                    )}
                    <button
                      onClick={removeFileHandler}
                      className="p-2 rounded-lg hover:bg-glass-hover transition-colors"
                    >
                      <X className="w-4 h-4 text-text-muted hover:text-accent-error" />
                    </button>
                  </div>
                </div>
              </div>

              {/* View Data Button */}
              {uploadedFile.preview_available && (
                <button
                  onClick={() => setShowDataPreview(true)}
                  className="w-full bg-gradient-to-r from-accent-secondary to-accent-tertiary text-white font-semibold py-3 px-6 rounded-xl transition-all duration-300 hover:shadow-glass-lg hover:transform hover:scale-[1.02] flex items-center justify-center gap-2"
                >
                  <File className="w-4 h-4" />
                  View Data Preview
                </button>
              )}

              {/* Validation Errors */}
              {uploadedFile.validation_results.errors.length > 0 && (
                <div className="p-3 bg-accent-error/10 border border-accent-error/20 rounded-lg">
                  <div className="flex items-start gap-2">
                    <AlertCircle className="w-4 h-4 text-accent-error mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="text-sm font-medium text-accent-error">Validation Issues</p>
                      <ul className="text-xs text-text-secondary mt-1 space-y-1">
                        {uploadedFile.validation_results.errors.map((error, index) => (
                          <li key={index}>• {error}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
          
          <div className="text-xs mt-4 text-text-muted text-center">
            Supported formats: CSV, Excel (XLSX/XLS), JSON
          </div>
        </div>

        {/* Ask Copilot Card */}
        <div className="card-glass p-6 animate-slide-in" style={{ animationDelay: '0.1s' }}>
          <h2 className="text-2xl font-bold text-text-primary mb-6 flex items-center gap-3">
            <Send className="w-6 h-6 text-accent-secondary" />
            Ask Copilot
          </h2>
          
          <div className="space-y-4">
            <textarea
              className="w-full bg-glass-bg border border-glass-border text-text-primary rounded-xl p-4 resize-none focus:border-accent-primary focus:ring-1 focus:ring-accent-primary transition-all duration-300 placeholder:text-text-muted"
              placeholder="Ask me anything about your data..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              rows={4}
            />
            
            <button
              onClick={handleSendQuery}
              disabled={!input.trim() || isProcessing}
              className="w-full bg-gradient-to-r from-accent-primary to-accent-secondary text-white font-semibold py-3 px-6 rounded-xl transition-all duration-300 hover:shadow-glass-lg hover:transform hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none disabled:shadow-none flex items-center justify-center gap-2"
            >
              <Send className="w-4 h-4" />
              {isProcessing ? 'Processing...' : 'Send Query'}
            </button>
          </div>

          <div className="mt-4 text-xs text-text-muted">
            <p className="mb-2">Try asking:</p>
            <ul className="space-y-1 list-disc list-inside text-text-muted">
              <li>"Show me sales trends by region"</li>
              <li>"What are the top performing products?"</li>
              <li>"Create a dashboard for quarterly revenue"</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Right Side - Agent Workflow */}
      <div className="w-[450px] card-glass p-6 animate-slide-in" style={{ animationDelay: '0.2s' }}>
        <h2 className="text-2xl font-bold text-text-primary mb-6 flex items-center gap-3">
          <div className="w-6 h-6 rounded-full bg-gradient-to-r from-accent-secondary to-accent-primary" />
          Agent Workflow
        </h2>
        
        <div className="mb-4 text-sm text-text-secondary">
          Multi-agent AI system processing your requests
        </div>
        
        <AgentList />
        
        <div className="mt-6 p-4 bg-glass-bg rounded-xl border border-glass-border">
          <div className="flex items-center justify-between text-sm">
            <span className="text-text-muted">System Status</span>
            <span className={`font-medium ${isConnected ? 'text-accent-tertiary' : 'text-accent-error'}`}>
              {isConnected ? 'Ready' : 'Offline'}
            </span>
          </div>
          <div className="mt-2 w-full bg-dark-tertiary rounded-full h-2">
            <div className={`h-2 rounded-full transition-all duration-500 ${
              isConnected 
                ? 'bg-gradient-to-r from-accent-tertiary to-accent-primary w-full' 
                : 'bg-accent-error w-1/4'
            }`} />
          </div>
        </div>
      </div>
    </div>
    ) : (
      /* Data Preview View */
      <div className="min-h-screen p-6 animate-fade-in">
        <div className="max-w-7xl mx-auto">
          {/* Header with Back Button */}
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-4">
              <button
                onClick={() => setShowDataPreview(false)}
                className="p-3 bg-glass-bg border border-glass-border rounded-xl hover:bg-glass-hover transition-all duration-300 hover:shadow-glass"
              >
                <X className="w-5 h-5 text-text-secondary" />
              </button>
              <div>
                <h1 className="text-3xl font-bold text-text-primary">Data Analysis</h1>
                <p className="text-text-secondary mt-1">
                  {uploadedFile?.filename} • {formatFileSize(uploadedFile?.size || 0)}
                </p>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              <button
                onClick={removeFileHandler}
                className="px-4 py-2 bg-accent-error/20 text-accent-error border border-accent-error/30 rounded-lg hover:bg-accent-error/30 transition-colors flex items-center gap-2"
              >
                <X className="w-4 h-4" />
                Remove File
              </button>
            </div>
          </div>

          {/* Data Preview Content */}
          {previewError ? (
            <div className="card-glass p-6">
              <div className="flex items-start gap-3">
                <AlertCircle className="w-6 h-6 text-accent-error mt-1 flex-shrink-0" />
                <div>
                  <h3 className="text-lg font-semibold text-accent-error mb-2">Failed to Load Data</h3>
                  <p className="text-text-secondary">{previewError}</p>
                  <button
                    onClick={() => window.location.reload()}
                    className="mt-3 px-4 py-2 bg-accent-primary text-white rounded-lg hover:bg-accent-primary/80 transition-colors"
                  >
                    Try Again
                  </button>
                </div>
              </div>
            </div>
          ) : preview && statistics ? (
            <DataPreview 
              preview={preview} 
              statistics={statistics} 
              isLoading={previewLoading} 
            />
          ) : (
            <div className="card-glass p-8 text-center">
              <div className="w-16 h-16 border-4 border-accent-primary border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
              <h3 className="text-xl font-semibold text-text-primary mb-2">Processing Your Data</h3>
              <p className="text-text-secondary">Analyzing data structure and generating insights...</p>
            </div>
          )}
        </div>
      </div>
    )}
    </div>
  );
}
