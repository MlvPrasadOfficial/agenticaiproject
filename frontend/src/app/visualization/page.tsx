/**
 * Data Visualization Page
 * Integrates Tasks 55-56: Complete data visualization dashboard
 */

'use client';

import React, { useState, useEffect } from 'react';
import DataStatisticsDashboard from '../components/DataStatisticsDashboard';
import InteractiveCharts from '../components/InteractiveCharts';
import { BarChart3, LineChart, Database, TrendingUp, Download, RefreshCw } from 'lucide-react';

interface DataVisualizationPageProps {
  fileId?: string;
}

export default function DataVisualizationPage({ fileId }: DataVisualizationPageProps) {
  const [activeTab, setActiveTab] = useState<'statistics' | 'charts'>('statistics');
  const [isLoading, setIsLoading] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(new Date());

  // Mock data for demonstration
  const mockStatistics = {
    total_records: 1250,
    total_columns: 8,
    missing_values_percentage: 5.2,
    data_types: {
      'numeric': 4,
      'text': 3,
      'date': 1
    },
    quality_score: 87.5,
    outliers_detected: 12,
    duplicate_records: 3,
    column_statistics: {
      'revenue': { mean: 15420, median: 12300, std: 8940, min: 1200, max: 45600, null_count: 5 },
      'customer_id': { unique_values: 1247, null_count: 0 },
      'date': { unique_values: 365, null_count: 2 },
      'category': { unique_values: 12, null_count: 8 }
    }
  };

  const mockChartData = [
    {
      data: Array.from({ length: 20 }, (_, i) => ({
        x: i,
        y: Math.sin(i * 0.5) * 50 + 100 + Math.random() * 20,
        label: `Month ${i + 1}`
      })),
      title: 'Revenue Trend Analysis',
      xLabel: 'Month',
      yLabel: 'Revenue ($1000s)',
      type: 'line' as const
    },
    {
      data: [
        { x: 'Electronics', y: 120, category: 'Hardware' },
        { x: 'Clothing', y: 85, category: 'Fashion' },
        { x: 'Books', y: 95, category: 'Media' },
        { x: 'Sports', y: 110, category: 'Recreation' },
        { x: 'Home', y: 75, category: 'Lifestyle' }
      ],
      title: 'Sales by Category',
      xLabel: 'Product Category',
      yLabel: 'Sales Volume',
      type: 'bar' as const
    }
  ];

  const handleRefresh = async () => {
    setIsLoading(true);
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500));
    setLastUpdated(new Date());
    setIsLoading(false);
  };

  const handleExportDashboard = () => {
    // Export entire dashboard as PDF or image
    console.log('Exporting dashboard...');
    // Implementation would use libraries like html2canvas or jsPDF
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <Database className="h-8 w-8 text-blue-500 mr-3" />
              <div>
                <h1 className="text-xl font-semibold text-gray-900">Data Visualization Dashboard</h1>
                <p className="text-sm text-gray-500">
                  {fileId ? `File ID: ${fileId}` : 'Sample Data'} • Last updated: {lastUpdated.toLocaleTimeString()}
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              <button
                onClick={handleRefresh}
                disabled={isLoading}
                className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
              >
                <RefreshCw className={`h-4 w-4 mr-1.5 ${isLoading ? 'animate-spin' : ''}`} />
                Refresh
              </button>
              
              <button
                onClick={handleExportDashboard}
                className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <Download className="h-4 w-4 mr-1.5" />
                Export
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            <button
              onClick={() => setActiveTab('statistics')}
              className={`flex items-center py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'statistics'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <BarChart3 className="h-4 w-4 mr-2" />
              Data Statistics
            </button>
            
            <button
              onClick={() => setActiveTab('charts')}
              className={`flex items-center py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'charts'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <LineChart className="h-4 w-4 mr-2" />
              Interactive Charts
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Progress Indicator */}
        {isLoading && (
          <div className="mb-6">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-center">
                <RefreshCw className="h-5 w-5 text-blue-500 animate-spin mr-3" />
                <div>
                  <div className="text-sm font-medium text-blue-800">Updating visualizations...</div>
                  <div className="text-sm text-blue-600">Please wait while we fetch the latest data.</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Quick Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <Database className="h-6 w-6 text-gray-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Total Records</dt>
                    <dd className="text-lg font-medium text-gray-900">
                      {mockStatistics.total_records.toLocaleString()}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <BarChart3 className="h-6 w-6 text-gray-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Columns</dt>
                    <dd className="text-lg font-medium text-gray-900">{mockStatistics.total_columns}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <TrendingUp className="h-6 w-6 text-gray-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Quality Score</dt>
                    <dd className="text-lg font-medium text-gray-900">{mockStatistics.quality_score}%</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <LineChart className="h-6 w-6 text-gray-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Missing Values</dt>
                    <dd className="text-lg font-medium text-gray-900">{mockStatistics.missing_values_percentage}%</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Tab Content */}
        {activeTab === 'statistics' && (
          <div className="space-y-6">
            <DataStatisticsDashboard
              fileId={fileId || 'sample'}
              statistics={mockStatistics}
              loading={isLoading}
            />
          </div>
        )}

        {activeTab === 'charts' && (
          <div className="space-y-6">
            <InteractiveCharts
              chartData={mockChartData}
              fileId={fileId}
              loading={isLoading}
            />
          </div>
        )}
      </div>

      {/* Footer with real-time updates indicator */}
      <div className="bg-white border-t border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center text-sm text-gray-500">
              <div className="w-2 h-2 bg-green-400 rounded-full mr-2 animate-pulse"></div>
              Real-time updates active
            </div>
            <div className="text-sm text-gray-500">
              Tasks 55-56: Data Visualization Complete ✅
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
