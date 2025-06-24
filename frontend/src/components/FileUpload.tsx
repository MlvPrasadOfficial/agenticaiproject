"use client";

import React, { useState, useRef } from 'react';
import { Upload, File, X, CheckCircle, AlertCircle } from 'lucide-react';
import { apiClient, type UploadResponse } from '@/lib/api';
import { formatFileSize, isValidFileType, getFileTypeIcon } from '@/lib/utils';

interface FileUploadProps {
  onUploadComplete: (response: UploadResponse) => void;
  onUploadError: (error: string) => void;
}

interface UploadingFile {
  file: File;
  progress: number;
  status: 'uploading' | 'completed' | 'error';
  response?: UploadResponse;
  error?: string;
}

export function FileUpload({ onUploadComplete, onUploadError }: FileUploadProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [uploadingFiles, setUploadingFiles] = useState<UploadingFile[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDragIn = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(true);
  };

  const handleDragOut = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);

    const files = Array.from(e.dataTransfer.files);
    handleFiles(files);
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files ? Array.from(e.target.files) : [];
    handleFiles(files);
  };

  const handleFiles = async (files: File[]) => {
    const validFiles = files.filter(file => {
      if (!isValidFileType(file)) {
        onUploadError(`Invalid file type: ${file.name}`);
        return false;
      }
      if (file.size > 100 * 1024 * 1024) { // 100MB limit
        onUploadError(`File too large: ${file.name} (max 100MB)`);
        return false;
      }
      return true;
    });

    if (validFiles.length === 0) return;

    // Initialize uploading state
    const newUploadingFiles: UploadingFile[] = validFiles.map(file => ({
      file,
      progress: 0,
      status: 'uploading'
    }));

    setUploadingFiles(prev => [...prev, ...newUploadingFiles]);

    // Upload files sequentially
    for (let i = 0; i < validFiles.length; i++) {
      const file = validFiles[i];
      try {
        const response = await apiClient.uploadFile(file, (progress) => {
          setUploadingFiles(prev => prev.map(uf => 
            uf.file === file ? { ...uf, progress } : uf
          ));
        });

        setUploadingFiles(prev => prev.map(uf => 
          uf.file === file 
            ? { ...uf, status: 'completed', response, progress: 100 }
            : uf
        ));

        onUploadComplete(response);
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Upload failed';
        setUploadingFiles(prev => prev.map(uf => 
          uf.file === file 
            ? { ...uf, status: 'error', error: errorMessage }
            : uf
        ));
        onUploadError(errorMessage);
      }
    }
  };

  const removeFile = (fileToRemove: File) => {
    setUploadingFiles(prev => prev.filter(uf => uf.file !== fileToRemove));
  };

  const openFileDialog = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      {/* Drop Zone */}
      <div
        className={`
          relative border-2 border-dashed rounded-lg p-8 text-center transition-all duration-200 cursor-pointer
          ${isDragOver 
            ? 'border-blue-400 bg-blue-50 dark:bg-blue-950/20' 
            : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500'
          }
        `}
        onDragEnter={handleDragIn}
        onDragLeave={handleDragOut}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={openFileDialog}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".csv,.xlsx,.xls,.json,.parquet"
          onChange={handleFileSelect}
          className="hidden"
        />
        
        <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
          Upload your data files
        </h3>
        <p className="text-gray-500 dark:text-gray-400 mb-4">
          Drag and drop files here, or click to browse
        </p>
        <p className="text-sm text-gray-400 dark:text-gray-500">
          Supported formats: CSV, Excel, JSON, Parquet (max 100MB)
        </p>
      </div>

      {/* Uploading Files List */}
      {uploadingFiles.length > 0 && (
        <div className="mt-6 space-y-3">
          <h4 className="font-medium text-gray-900 dark:text-gray-100">
            Uploading Files
          </h4>
          {uploadingFiles.map((uploadingFile, index) => (
            <div
              key={`${uploadingFile.file.name}-${index}`}
              className="flex items-center space-x-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg"
            >
              <div className="text-2xl">
                {getFileTypeIcon(uploadingFile.file.name)}
              </div>
              
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between mb-1">
                  <p className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                    {uploadingFile.file.name}
                  </p>
                  <span className="text-xs text-gray-500">
                    {formatFileSize(uploadingFile.file.size)}
                  </span>
                </div>
                
                {uploadingFile.status === 'uploading' && (
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${uploadingFile.progress}%` }}
                    />
                  </div>
                )}
                
                {uploadingFile.status === 'completed' && (
                  <div className="flex items-center text-green-600 dark:text-green-400">
                    <CheckCircle className="h-4 w-4 mr-1" />
                    <span className="text-xs">Upload completed</span>
                  </div>
                )}
                
                {uploadingFile.status === 'error' && (
                  <div className="flex items-center text-red-600 dark:text-red-400">
                    <AlertCircle className="h-4 w-4 mr-1" />
                    <span className="text-xs">{uploadingFile.error}</span>
                  </div>
                )}
              </div>
              
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  removeFile(uploadingFile.file);
                }}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
