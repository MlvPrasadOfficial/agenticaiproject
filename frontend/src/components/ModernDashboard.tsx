'use client';

import React, { useState } from 'react';
import { FileText, MessageSquare, BarChart3, Settings } from 'lucide-react';
import { HealthIndicator } from './ui/health-indicator';
import FileUploadQueue from './ui/file-upload-queue';
import { UploadedFile } from './ui/file-upload';
import DataTable, { DataColumn } from './ui/data-table';

export default function ModernDashboard() {
  const [activeTab, setActiveTab] = useState<'upload' | 'data' | 'chat' | 'settings'>('upload');
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [tableData, setTableData] = useState<Record<string, any>[]>([]);
  const [tableColumns, setTableColumns] = useState<DataColumn[]>([]);

  const handleUploadComplete = (files: UploadedFile[]) => {
    // In a real app, this would process the uploaded files and convert to table data
    console.log('Upload completed:', files);
    
    // Mock data for demonstration
    const mockData = [
      { id: 1, name: 'Product A', sales: 15000, region: 'North', date: '2024-01-15' },
      { id: 2, name: 'Product B', sales: 23000, region: 'South', date: '2024-01-16' },
      { id: 3, name: 'Product C', sales: 18500, region: 'East', date: '2024-01-17' },
      { id: 4, name: 'Product D', sales: 31000, region: 'West', date: '2024-01-18' },
      { id: 5, name: 'Product E', sales: 12000, region: 'North', date: '2024-01-19' },
    ];

    const mockColumns: DataColumn[] = [
      { key: 'id', label: 'ID', type: 'number', width: 80 },
      { key: 'name', label: 'Product Name', type: 'string' },
      { key: 'sales', label: 'Sales', type: 'number', format: (value) => `$${value.toLocaleString()}` },
      { key: 'region', label: 'Region', type: 'string' },
      { key: 'date', label: 'Date', type: 'date' },
    ];

    setTableData(mockData);
    setTableColumns(mockColumns);
    setActiveTab('data');
  };

  const handleUploadError = (error: string) => {
    console.error('Upload error:', error);
  };

  const handleDataExport = (data: Record<string, any>[]) => {
    const csvContent = convertToCSV(data);
    downloadCSV(csvContent, 'exported_data.csv');
  };

  const convertToCSV = (data: Record<string, any>[]): string => {
    if (data.length === 0) return '';
    
    const headers = Object.keys(data[0]);
    const csvHeaders = headers.join(',');
    const csvRows = data.map(row => 
      headers.map(header => `"${row[header]}"`).join(',')
    );
    
    return [csvHeaders, ...csvRows].join('\n');
  };

  const downloadCSV = (content: string, filename: string) => {
    const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    if (link.download !== undefined) {
      const url = URL.createObjectURL(blob);
      link.setAttribute('href', url);
      link.setAttribute('download', filename);
      link.style.visibility = 'hidden';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  const tabs = [
    { id: 'upload' as const, label: 'Upload Data', icon: FileText },
    { id: 'data' as const, label: 'Data View', icon: BarChart3 },
    { id: 'chat' as const, label: 'AI Chat', icon: MessageSquare },
    { id: 'settings' as const, label: 'Settings', icon: Settings },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg"></div>
                <h1 className="text-xl font-bold text-gray-900 dark:text-gray-100">
                  Enterprise Insights
                </h1>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <HealthIndicator />
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tab Navigation */}
        <div className="mb-8">
          <div className="border-b border-gray-200 dark:border-gray-700">
            <nav className="-mb-px flex space-x-8">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                      activeTab === tab.id
                        ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    <span>{tab.label}</span>
                  </button>
                );
              })}
            </nav>
          </div>
        </div>

        {/* Tab Content */}
        <div className="space-y-8">
          {activeTab === 'upload' && (
            <div className="space-y-6">
              <div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
                  Upload Your Data
                </h2>
                <p className="text-gray-600 dark:text-gray-400">
                  Upload CSV, Excel, or JSON files to get started with data analysis.
                </p>
              </div>
              
              <FileUploadQueue
                onUploadComplete={handleUploadComplete}
                onUploadError={handleUploadError}
                className="max-w-4xl"
              />
            </div>
          )}

          {activeTab === 'data' && (
            <div className="space-y-6">
              <div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
                  Data Analysis
                </h2>
                <p className="text-gray-600 dark:text-gray-400">
                  Explore and analyze your uploaded data with interactive tables and charts.
                </p>
              </div>

              {tableData.length > 0 ? (
                <DataTable
                  data={tableData}
                  columns={tableColumns}
                  title="Dataset Preview"
                  searchable={true}
                  exportable={true}
                  selectable={true}
                  pagination={true}
                  pageSize={25}
                  onExport={handleDataExport}
                />
              ) : (
                <div className="text-center py-12">
                  <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
                    No Data Available
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400 mb-4">
                    Upload a file to see your data here.
                  </p>
                  <button
                    onClick={() => setActiveTab('upload')}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    Upload Data
                  </button>
                </div>
              )}
            </div>
          )}

          {activeTab === 'chat' && (
            <div className="space-y-6">
              <div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
                  AI Assistant
                </h2>
                <p className="text-gray-600 dark:text-gray-400">
                  Chat with our AI assistant to get insights from your data.
                </p>
              </div>

              <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
                <div className="text-center py-12">
                  <MessageSquare className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
                    AI Chat Coming Soon
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400">
                    The conversational AI interface will be available in the next update.
                  </p>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'settings' && (
            <div className="space-y-6">
              <div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
                  Settings
                </h2>
                <p className="text-gray-600 dark:text-gray-400">
                  Configure your preferences and application settings.
                </p>
              </div>

              <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
                <div className="text-center py-12">
                  <Settings className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
                    Settings Panel Coming Soon
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400">
                    Configuration options will be available in the next update.
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
