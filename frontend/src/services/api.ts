/**
 * API service layer for Enterprise Insights Copilot frontend
 * Handles all backend communication with proper error handling and type safety
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

// Types for API responses
export interface FileUploadResponse {
  file_id: string;
  filename: string;
  size: number;
  mime_type: string;
  status: string;
  upload_timestamp: string;
  validation_results: {
    errors: string[];
    warnings: string[];
  };
  preview_available: boolean;
  metadata: Record<string, any>;
}

export interface DataPreviewResponse {
  file_id: string;
  filename: string;
  total_rows: number;
  total_columns: number;
  preview_rows: number;
  columns: Array<{
    name: string;
    type: string;
    non_null_count: number;
    null_percentage: number;
  }>;
  data: Array<Record<string, any>>;
  has_more: boolean;
}

export interface DataStatisticsResponse {
  file_id: string;
  filename: string;
  overall_stats: {
    total_rows: number;
    total_columns: number;
    memory_usage_mb: number;
    data_quality_score: number;
  };
  column_statistics: Array<{
    name: string;
    type: string;
    statistics: Record<string, any>;
    quality_score: number;
    issues: string[];
  }>;
  data_quality: {
    completeness_score: number;
    consistency_score: number;
    validity_score: number;
    uniqueness_score: number;
    issues: string[];
  };
  recommendations: string[];
}

export interface ApiError {
  detail: string;
  status_code: number;
}

// Custom error class for API errors
export class ApiException extends Error {
  constructor(public status: number, public detail: string) {
    super(detail);
    this.name = 'ApiException';
  }
}

// Generic API request handler with error handling
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({
        detail: `HTTP ${response.status}: ${response.statusText}`,
      }));
      throw new ApiException(response.status, errorData.detail || 'Unknown error');
    }

    return await response.json();
  } catch (error) {
    if (error instanceof ApiException) {
      throw error;
    }
    
    // Network or other errors
    console.error('API request failed:', error);
    throw new ApiException(0, 'Network error: Unable to connect to server');
  }
}

// File upload with progress tracking
export async function uploadFile(
  file: File,
  onProgress?: (progress: number) => void
): Promise<FileUploadResponse> {
  const formData = new FormData();
  formData.append('file', file);

  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();

    // Track upload progress
    if (onProgress) {
      xhr.upload.addEventListener('progress', (event) => {
        if (event.lengthComputable) {
          const progress = (event.loaded / event.total) * 100;
          onProgress(progress);
        }
      });
    }

    xhr.addEventListener('load', () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          const response = JSON.parse(xhr.responseText);
          // The backend returns an array, so take the first item
          resolve(Array.isArray(response) ? response[0] : response);
        } catch (error) {
          reject(new ApiException(xhr.status, 'Invalid response format'));
        }
      } else {
        try {
          const errorData = JSON.parse(xhr.responseText);
          reject(new ApiException(xhr.status, errorData.detail || 'Upload failed'));
        } catch {
          reject(new ApiException(xhr.status, `HTTP ${xhr.status}: ${xhr.statusText}`));
        }
      }
    });

    xhr.addEventListener('error', () => {
      reject(new ApiException(0, 'Network error during upload'));
    });

    xhr.open('POST', `${API_BASE_URL}/api/v1/files/upload`);
    xhr.send(formData);
  });
}

// Get data preview
export async function getDataPreview(
  fileId: string,
  rows: number = 10
): Promise<DataPreviewResponse> {
  return apiRequest<DataPreviewResponse>(
    `/api/v1/data/preview/${fileId}?rows=${rows}`
  );
}

// Get data statistics
export async function getDataStatistics(fileId: string): Promise<DataStatisticsResponse> {
  return apiRequest<DataStatisticsResponse>(`/api/v1/data/statistics/${fileId}`);
}

// Get upload status
export async function getUploadStatus(fileId: string): Promise<{ file_id: string; status: string }> {
  return apiRequest<{ file_id: string; status: string }>(`/api/v1/files/upload-status/${fileId}`);
}

// Delete uploaded file
export async function deleteFile(fileId: string): Promise<{ file_id: string; status: string }> {
  return apiRequest<{ file_id: string; status: string }>(`/api/v1/files/files/${fileId}`, {
    method: 'DELETE',
  });
}

// Health check
export async function healthCheck(): Promise<{ status: string; timestamp: string }> {
  return apiRequest<{ status: string; timestamp: string }>('/health');
}

// Utility function to check if backend is available
export async function checkBackendConnection(): Promise<boolean> {
  try {
    await healthCheck();
    return true;
  } catch {
    return false;
  }
}
