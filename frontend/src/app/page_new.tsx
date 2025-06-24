"use client";

import React, { useState } from 'react';
import { Brain, Database, Zap, Upload as FileUploadIcon } from 'lucide-react';
import { FileUpload } from '@/components/FileUpload';
import { ChatInterface } from '@/components/ChatInterface';
import { Dashboard } from '@/components/Dashboard';
import { type UploadResponse } from '@/lib/api';

interface AppState {
  currentFileId?: string;
  currentFileName?: string;
  insights: Array<{
    id: string;
    title: string;
    description: string;
    type: 'trend' | 'correlation' | 'anomaly' | 'summary';
    value?: string | number;
    change?: number;
    metadata?: Record<string, unknown>;
  }>;
  visualizations: Array<{
    id: string;
    title: string;
    type: 'bar' | 'line' | 'pie' | 'scatter' | 'heatmap';
    data: unknown;
    config?: Record<string, unknown>;
  }>;
  fileInfo?: {
    name: string;
    size: number;
    rows: number;
    columns: number;
  };
}

export default function HomePage() {
  const [appState, setAppState] = useState<AppState>({
    insights: [],
    visualizations: [],
  });
  const [error, setError] = useState<string>('');

  const handleUploadComplete = (response: UploadResponse) => {
    setAppState(prev => ({
      ...prev,
      currentFileId: response.file_id,
      currentFileName: response.filename,
      fileInfo: {
        name: response.filename,
        size: 0, // Will be updated when we get actual file info
        rows: 0,
        columns: 0,
      }
    }));
    setError('');
  };

  const handleUploadError = (errorMessage: string) => {
    setError(errorMessage);
  };

  const handleInsightGenerated = (insight: unknown) => {
    // Type guard and transform insight data
    const newInsight = {
      id: Date.now().toString(),
      title: typeof insight === 'object' && insight !== null && 'title' in insight 
        ? String(insight.title) 
        : 'New Insight',
      description: typeof insight === 'object' && insight !== null && 'description' in insight 
        ? String(insight.description) 
        : 'AI-generated insight from your data',
      type: 'summary' as const,
      value: typeof insight === 'object' && insight !== null && 'value' in insight 
        ? insight.value as string | number
        : undefined,
    };

    setAppState(prev => ({
      ...prev,
      insights: [...prev.insights, newInsight],
    }));
  };

  const handleVisualizationGenerated = (visualization: unknown) => {
    // Type guard and transform visualization data
    const newVisualization = {
      id: Date.now().toString(),
      title: typeof visualization === 'object' && visualization !== null && 'title' in visualization 
        ? String(visualization.title) 
        : 'New Visualization',
      type: 'bar' as const,
      data: visualization,
      config: typeof visualization === 'object' && visualization !== null && 'config' in visualization 
        ? visualization.config as Record<string, unknown>
        : undefined,
    };

    setAppState(prev => ({
      ...prev,
      visualizations: [...prev.visualizations, newVisualization],
    }));
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-3">
              <div className="flex items-center space-x-2">
                <Brain className="h-8 w-8 text-blue-600" />
                <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                  Enterprise Insights Copilot
                </h1>
              </div>
            </div>
            <div className="flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400">
              <Database className="h-4 w-4" />
              <span>Powered by AI Multi-Agent System</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Hero Section */}
        {!appState.currentFileId && (
          <div className="text-center mb-12">
            <div className="flex justify-center mb-6">
              <div className="flex items-center space-x-4">
                <div className="p-3 bg-blue-100 dark:bg-blue-900/20 rounded-full">
                  <FileUploadIcon className="h-6 w-6 text-blue-600" />
                </div>
                <div className="h-px w-8 bg-gray-300 dark:bg-gray-600"></div>
                <div className="p-3 bg-green-100 dark:bg-green-900/20 rounded-full">
                  <Brain className="h-6 w-6 text-green-600" />
                </div>
                <div className="h-px w-8 bg-gray-300 dark:bg-gray-600"></div>
                <div className="p-3 bg-purple-100 dark:bg-purple-900/20 rounded-full">
                  <Zap className="h-6 w-6 text-purple-600" />
                </div>
              </div>
            </div>
            <h2 className="text-4xl font-bold text-gray-900 dark:text-gray-100 mb-4">
              AI-Powered Business Intelligence
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-400 mb-8 max-w-3xl mx-auto">
              Upload your data and let our multi-agent AI system analyze, visualize, and generate 
              insights automatically. From data profiling to executive reports, all powered by LLaMA 3.1.
            </p>
            
            {/* Features */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12 max-w-4xl mx-auto">
              <div className="p-6 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                <Database className="h-8 w-8 text-blue-600 mx-auto mb-4" />
                <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-2">
                  Smart Data Analysis
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Automatic data profiling, quality assessment, and statistical analysis
                </p>
              </div>
              <div className="p-6 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                <Brain className="h-8 w-8 text-green-600 mx-auto mb-4" />
                <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-2">
                  AI Insights
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Natural language queries with intelligent pattern recognition
                </p>
              </div>
              <div className="p-6 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                <Zap className="h-8 w-8 text-purple-600 mx-auto mb-4" />
                <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-2">
                  Auto Reports
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Professional reports and visualizations generated instantly
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
            <p className="text-red-800 dark:text-red-200">{error}</p>
          </div>
        )}

        {/* File Upload */}
        {!appState.currentFileId && (
          <div className="mb-12">
            <FileUpload 
              onUploadComplete={handleUploadComplete}
              onUploadError={handleUploadError}
            />
          </div>
        )}

        {/* Main Application Interface */}
        {appState.currentFileId && (
          <div className="space-y-8">
            {/* Current File Info */}
            <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-green-100 dark:bg-green-900/20 rounded">
                    <Database className="h-5 w-5 text-green-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900 dark:text-gray-100">
                      {appState.currentFileName}
                    </h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      File uploaded successfully - Ready for analysis
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => setAppState({ insights: [], visualizations: [] })}
                  className="text-sm text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300"
                >
                  Upload New File
                </button>
              </div>
            </div>

            {/* Dashboard and Chat Layout */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Chat Interface */}
              <div className="lg:col-span-1">
                <ChatInterface
                  fileId={appState.currentFileId}
                  onInsightGenerated={handleInsightGenerated}
                  onVisualizationGenerated={handleVisualizationGenerated}
                />
              </div>

              {/* Dashboard */}
              <div className="lg:col-span-1">
                <Dashboard
                  insights={appState.insights}
                  visualizations={appState.visualizations}
                  fileInfo={appState.fileInfo}
                />
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center text-sm text-gray-500 dark:text-gray-400">
            <p>Enterprise Insights Copilot - Powered by LLaMA 3.1 & Multi-Agent AI</p>
            <p className="mt-1">Built with FastAPI, Next.js, LangGraph & Pinecone</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
