'use client';

import React, { useState, useCallback, useRef } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, X, File, FileText, FileImage, FileSpreadsheet, AlertCircle, CheckCircle2 } from 'lucide-react';

export interface UploadedFile {
  id: string;
  file: File;
  status: 'uploading' | 'success' | 'error' | 'pending';
  progress: number;
  error?: string;
  preview?: string;
}

interface FileUploadProps {
  onFilesSelected: (files: File[]) => void;
  onFileRemove: (fileId: string) => void;
  maxFiles?: number;
  maxFileSize?: number; // in bytes
  acceptedFileTypes?: string[];
  multiple?: boolean;
  uploadedFiles?: UploadedFile[];
  className?: string;
}

const FileUpload: React.FC<FileUploadProps> = ({
  onFilesSelected,
  onFileRemove,
  maxFiles = 10,
  maxFileSize = 10 * 1024 * 1024, // 10MB default
  acceptedFileTypes = ['.csv', '.xlsx', '.xls', '.json', '.txt'],
  multiple = true,
  uploadedFiles = [],
  className = ''
}) => {
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const onDrop = useCallback((acceptedFiles: File[], rejectedFiles: any[]) => {
    if (acceptedFiles.length > 0) {
      onFilesSelected(acceptedFiles);
    }
    
    // Handle rejected files
    if (rejectedFiles.length > 0) {
      console.warn('Some files were rejected:', rejectedFiles);
    }
  }, [onFilesSelected]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: acceptedFileTypes.reduce((acc, type) => {
      const mimeType = getMimeType(type);
      if (mimeType) {
        acc[mimeType] = [type];
      }
      return acc;
    }, {} as Record<string, string[]>),
    maxSize: maxFileSize,
    maxFiles: maxFiles,
    multiple,
    onDragEnter: () => setDragActive(true),
    onDragLeave: () => setDragActive(false),
  });

  const handleFileInputClick = () => {
    fileInputRef.current?.click();
  };

  const getFileIcon = (fileName: string) => {
    const extension = fileName.toLowerCase().split('.').pop();
    switch (extension) {
      case 'csv':
      case 'xlsx':
      case 'xls':
        return <FileSpreadsheet className="w-8 h-8 text-green-500" />;
      case 'json':
      case 'txt':
        return <FileText className="w-8 h-8 text-blue-500" />;
      case 'jpg':
      case 'jpeg':
      case 'png':
      case 'gif':
        return <FileImage className="w-8 h-8 text-purple-500" />;
      default:
        return <File className="w-8 h-8 text-gray-500" />;
    }
  };

  const getStatusIcon = (status: UploadedFile['status']) => {
    switch (status) {
      case 'success':
        return <CheckCircle2 className="w-5 h-5 text-green-500" />;
      case 'error':
        return <AlertCircle className="w-5 h-5 text-red-500" />;
      case 'uploading':
        return (
          <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
        );
      default:
        return null;
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className={`w-full ${className}`}>
      {/* Professional Drop Zone */}
      <div
        {...getRootProps()}
        className={`
          relative border-2 border-dashed rounded-3xl p-12 text-center transition-all duration-500 cursor-pointer group
          ${isDragActive || dragActive 
            ? 'border-blue-500 bg-blue-500/10 scale-105 shadow-2xl' 
            : 'border-gray-300 dark:border-gray-600 hover:border-blue-400 dark:hover:border-blue-500 hover:bg-blue-50/30 dark:hover:bg-blue-900/10'
          }
          ${uploadedFiles.length > 0 ? 'mb-8' : ''}
          backdrop-blur-sm bg-white/20 dark:bg-gray-800/20 shadow-xl hover:shadow-2xl
        `}
      >
        <input {...getInputProps()} ref={fileInputRef} />
        
        {/* Animated Background Elements */}
        <div className="absolute inset-0 rounded-3xl overflow-hidden">
          <div className={`absolute top-0 left-1/4 w-32 h-32 bg-blue-500/10 rounded-full filter blur-xl transition-all duration-700 ${
            isDragActive ? 'animate-pulse scale-150' : 'group-hover:scale-125'
          }`}></div>
          <div className={`absolute bottom-0 right-1/4 w-24 h-24 bg-purple-500/10 rounded-full filter blur-xl transition-all duration-700 ${
            isDragActive ? 'animate-pulse scale-150' : 'group-hover:scale-125'
          }`} style={{ animationDelay: '0.5s' }}></div>
        </div>
        
        <div className="relative z-10 flex flex-col items-center space-y-6">
          {/* Enhanced Upload Icon */}
          <div className={`
            relative p-6 rounded-2xl transition-all duration-500
            ${isDragActive || dragActive 
              ? 'bg-gradient-to-br from-blue-500 to-purple-600 text-white scale-110 shadow-lg' 
              : 'bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-700 dark:to-gray-800 text-gray-600 dark:text-gray-300 group-hover:scale-110'
            }
          `}>
            <Upload className={`w-12 h-12 transition-all duration-500 ${
              isDragActive ? 'animate-bounce' : 'group-hover:rotate-12'
            }`} />
            
            {/* Icon Glow Effect */}
            <div className={`absolute inset-0 rounded-2xl transition-opacity duration-500 ${
              isDragActive 
                ? 'bg-blue-500/30 opacity-100' 
                : 'bg-gradient-to-br from-blue-500/20 to-purple-500/20 opacity-0 group-hover:opacity-50'
            }`}></div>
          </div>
          
          {/* Professional Text Content */}
          <div className="space-y-4 max-w-md">
            <h3 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
              {isDragActive ? 'Drop your files here' : 'Upload Data Files'}
            </h3>
            <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
              {isDragActive 
                ? 'Release to upload your files instantly' 
                : 'Drag and drop your files here, or click to browse and select files from your computer'
              }
            </p>
            
            {/* Action Button */}
            {!isDragActive && (
              <button
                type="button"
                onClick={handleFileInputClick}
                className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105"
              >
                <Upload className="w-5 h-5 mr-2" />
                Choose Files
              </button>
            )}
          </div>
          
          {/* Enhanced File Type Badges */}
          <div className="flex flex-wrap justify-center gap-3 max-w-lg">
            {acceptedFileTypes.map((type) => (
              <span 
                key={type}
                className="px-3 py-1.5 text-xs font-medium bg-white/50 dark:bg-gray-700/50 text-gray-700 dark:text-gray-300 rounded-full border border-white/20 dark:border-gray-600/20 backdrop-blur-sm"
              >
                {type.replace('.', '').toUpperCase()}
              </span>
            ))}
          </div>
          
          {/* Professional Upload Stats */}
          <div className="grid grid-cols-3 gap-6 text-center text-sm">
            <div className="space-y-1">
              <div className="flex items-center justify-center">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                <span className="font-medium text-gray-700 dark:text-gray-300">Max Files</span>
              </div>
              <div className="text-gray-500 dark:text-gray-400">{maxFiles}</div>
            </div>
            <div className="space-y-1">
              <div className="flex items-center justify-center">
                <div className="w-2 h-2 bg-blue-500 rounded-full mr-2"></div>
                <span className="font-medium text-gray-700 dark:text-gray-300">Max Size</span>
              </div>
              <div className="text-gray-500 dark:text-gray-400">{formatFileSize(maxFileSize)}</div>
            </div>
            <div className="space-y-1">
              <div className="flex items-center justify-center">
                <div className="w-2 h-2 bg-purple-500 rounded-full mr-2"></div>
                <span className="font-medium text-gray-700 dark:text-gray-300">Security</span>
              </div>
              <div className="text-gray-500 dark:text-gray-400">Encrypted</div>
            </div>
          </div>
        </div>
      </div>

      {/* File List */}
      {uploadedFiles.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-sm font-medium text-gray-900 dark:text-gray-100">
            Files ({uploadedFiles.length})
          </h3>
          
          <div className="space-y-2">
            {uploadedFiles.map((uploadedFile) => (
              <div
                key={uploadedFile.id}
                className="flex items-center p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700"
              >
                {/* File Icon */}
                <div className="flex-shrink-0 mr-4">
                  {getFileIcon(uploadedFile.file.name)}
                </div>
                
                {/* File Info */}
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                    {uploadedFile.file.name}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {formatFileSize(uploadedFile.file.size)}
                  </p>
                  
                  {/* Progress Bar */}
                  {uploadedFile.status === 'uploading' && (
                    <div className="mt-2">
                      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
                        <div 
                          className="bg-blue-600 h-1.5 rounded-full transition-all duration-300"
                          style={{ width: `${uploadedFile.progress}%` }}
                        />
                      </div>
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        {uploadedFile.progress}%
                      </p>
                    </div>
                  )}
                  
                  {/* Error Message */}
                  {uploadedFile.status === 'error' && uploadedFile.error && (
                    <p className="text-xs text-red-500 mt-1">{uploadedFile.error}</p>
                  )}
                </div>
                
                {/* Status Icon */}
                <div className="flex-shrink-0 ml-4">
                  {getStatusIcon(uploadedFile.status)}
                </div>
                
                {/* Remove Button */}
                <button
                  onClick={() => onFileRemove(uploadedFile.id)}
                  className="flex-shrink-0 ml-2 p-1 text-gray-400 hover:text-red-500 transition-colors"
                  title="Remove file"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

// Helper function to get MIME type from file extension
function getMimeType(extension: string): string | null {
  const mimeTypes: Record<string, string> = {
    '.csv': 'text/csv',
    '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    '.xls': 'application/vnd.ms-excel',
    '.json': 'application/json',
    '.txt': 'text/plain',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png',
    '.gif': 'image/gif',
  };
  
  return mimeTypes[extension.toLowerCase()] || null;
}

export default FileUpload;
