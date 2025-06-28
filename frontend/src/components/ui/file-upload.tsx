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
      {/* Drop Zone */}
      <div
        {...getRootProps()}
        className={`
          relative border-2 border-dashed rounded-xl p-8 text-center transition-all duration-300 cursor-pointer
          ${isDragActive || dragActive 
            ? 'border-blue-500 bg-blue-50 dark:bg-blue-950/20' 
            : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500'
          }
          ${uploadedFiles.length > 0 ? 'mb-6' : ''}
        `}
      >
        <input {...getInputProps()} ref={fileInputRef} />
        
        <div className="flex flex-col items-center space-y-4">
          <div className={`
            p-4 rounded-full transition-colors duration-300
            ${isDragActive || dragActive 
              ? 'bg-blue-100 dark:bg-blue-900/30' 
              : 'bg-gray-100 dark:bg-gray-800'
            }
          `}>
            <Upload className={`w-8 h-8 ${isDragActive || dragActive ? 'text-blue-600' : 'text-gray-500'}`} />
          </div>
          
          <div>
            <p className="text-lg font-semibold text-gray-900 dark:text-gray-100">
              {isDragActive ? 'Drop files here' : 'Drag & drop files here'}
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              or{' '}
              <button
                type="button"
                onClick={handleFileInputClick}
                className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 font-medium"
              >
                browse files
              </button>
            </p>
          </div>
          
          <div className="text-xs text-gray-400 dark:text-gray-500 space-y-1">
            <p>Supported formats: {acceptedFileTypes.join(', ')}</p>
            <p>Max file size: {formatFileSize(maxFileSize)}</p>
            {multiple && <p>Max files: {maxFiles}</p>}
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
