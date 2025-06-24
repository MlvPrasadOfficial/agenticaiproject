"use client";

import React, { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, Users, DollarSign, Activity, FileText, Download } from 'lucide-react';

interface Insight {
  id: string;
  title: string;
  description: string;
  type: 'trend' | 'correlation' | 'anomaly' | 'summary';
  value?: string | number;
  change?: number;
  metadata?: Record<string, unknown>;
}

interface Visualization {
  id: string;
  title: string;
  type: 'bar' | 'line' | 'pie' | 'scatter' | 'heatmap';
  data: unknown;
  config?: Record<string, unknown>;
}

interface DashboardProps {
  insights: Insight[];
  visualizations: Visualization[];
  fileInfo?: {
    name: string;
    size: number;
    rows: number;
    columns: number;
  };
}

export function Dashboard({ insights, visualizations, fileInfo }: DashboardProps) {
  const [selectedVisualization, setSelectedVisualization] = useState<Visualization | null>(null);

  const getInsightIcon = (type: string) => {
    switch (type) {
      case 'trend':
        return <TrendingUp className="h-5 w-5 text-green-600" />;
      case 'correlation':
        return <Activity className="h-5 w-5 text-blue-600" />;
      case 'anomaly':
        return <FileText className="h-5 w-5 text-red-600" />;
      default:
        return <BarChart3 className="h-5 w-5 text-gray-600" />;
    }
  };

  const formatChange = (change: number) => {
    const sign = change >= 0 ? '+' : '';
    const color = change >= 0 ? 'text-green-600' : 'text-red-600';
    return <span className={color}>{sign}{change.toFixed(1)}%</span>;
  };

  return (
    <div className="w-full space-y-6">
      {/* Header Stats */}
      {fileInfo && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
            <div className="flex items-center">
              <FileText className="h-5 w-5 text-blue-600 mr-2" />
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">File</p>
                <p className="font-semibold text-gray-900 dark:text-gray-100 truncate">
                  {fileInfo.name}
                </p>
              </div>
            </div>
          </div>
          
          <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
            <div className="flex items-center">
              <Users className="h-5 w-5 text-green-600 mr-2" />
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Rows</p>
                <p className="font-semibold text-gray-900 dark:text-gray-100">
                  {fileInfo.rows.toLocaleString()}
                </p>
              </div>
            </div>
          </div>
          
          <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
            <div className="flex items-center">
              <BarChart3 className="h-5 w-5 text-purple-600 mr-2" />
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Columns</p>
                <p className="font-semibold text-gray-900 dark:text-gray-100">
                  {fileInfo.columns}
                </p>
              </div>
            </div>
          </div>
          
          <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
            <div className="flex items-center">
              <DollarSign className="h-5 w-5 text-yellow-600 mr-2" />
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Size</p>
                <p className="font-semibold text-gray-900 dark:text-gray-100">
                  {(fileInfo.size / (1024 * 1024)).toFixed(1)} MB
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Insights Section */}
      {insights.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
            Key Insights
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {insights.map((insight) => (
              <div
                key={insight.id}
                className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    {getInsightIcon(insight.type)}
                    <span className="text-sm font-medium text-gray-500 dark:text-gray-400 capitalize">
                      {insight.type}
                    </span>
                  </div>
                  {insight.change !== undefined && (
                    <div className="text-sm">
                      {formatChange(insight.change)}
                    </div>
                  )}
                </div>
                
                <h4 className="font-semibold text-gray-900 dark:text-gray-100 mb-1">
                  {insight.title}
                </h4>
                
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                  {insight.description}
                </p>
                
                {insight.value && (
                  <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                    {insight.value}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Visualizations Section */}
      {visualizations.length > 0 && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
              Visualizations
            </h3>
            <button
              className="flex items-center space-x-1 px-3 py-1 text-sm text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300"
            >
              <Download className="h-4 w-4" />
              <span>Export All</span>
            </button>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {visualizations.map((viz) => (
              <div
                key={viz.id}
                className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700 cursor-pointer hover:shadow-md transition-shadow"
                onClick={() => setSelectedVisualization(viz)}
              >
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-semibold text-gray-900 dark:text-gray-100">
                    {viz.title}
                  </h4>
                  <span className="text-xs text-gray-500 dark:text-gray-400 capitalize px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded">
                    {viz.type}
                  </span>
                </div>
                
                {/* Placeholder for actual chart */}
                <div className="h-48 bg-gray-50 dark:bg-gray-700 rounded flex items-center justify-center">
                  <div className="text-center">
                    <BarChart3 className="h-12 w-12 text-gray-400 mx-auto mb-2" />
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {viz.type.charAt(0).toUpperCase() + viz.type.slice(1)} Chart
                    </p>
                    <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
                      Click to view details
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {insights.length === 0 && visualizations.length === 0 && (
        <div className="text-center py-12">
          <BarChart3 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
            No insights yet
          </h3>
          <p className="text-gray-500 dark:text-gray-400">
            Upload a data file and start asking questions to see insights and visualizations here.
          </p>
        </div>
      )}

      {/* Visualization Modal */}
      {selectedVisualization && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
                  {selectedVisualization.title}
                </h3>
                <button
                  onClick={() => setSelectedVisualization(null)}
                  className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                >
                  ×
                </button>
              </div>
              
              {/* Full-size chart placeholder */}
              <div className="h-96 bg-gray-50 dark:bg-gray-700 rounded flex items-center justify-center">
                <div className="text-center">
                  <BarChart3 className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                  <p className="text-lg text-gray-500 dark:text-gray-400">
                    Full-size {selectedVisualization.type} chart would render here
                  </p>
                  <div className="mt-4 flex space-x-2 justify-center">
                    <button className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
                      Download PNG
                    </button>
                    <button className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700">
                      Download SVG
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
