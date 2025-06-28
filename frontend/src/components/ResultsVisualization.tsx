'use client';

import React, { useState, useEffect } from 'react';
import { 
  BarChart3, 
  PieChart, 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  Target,
  CheckCircle,
  AlertCircle,
  Info,
  Zap,
  Filter,
  Download,
  Maximize2,
  Eye
} from 'lucide-react';
import * as d3 from 'd3';

interface AnalysisResult {
  id: string;
  type: 'chart' | 'metric' | 'insight' | 'recommendation';
  title: string;
  description: string;
  data: any;
  confidence: number;
  timestamp: Date;
  metadata?: {
    agentType?: string;
    executionTime?: number;
    dataSource?: string;
  };
}

interface ResultsVisualizationProps {
  results: AnalysisResult[];
  onResultSelect?: (result: AnalysisResult) => void;
  onExport?: (result: AnalysisResult) => void;
  className?: string;
  layout?: 'grid' | 'list';
}

export default function ResultsVisualization({
  results,
  onResultSelect,
  onExport,
  className = '',
  layout = 'grid'
}: ResultsVisualizationProps) {
  const [selectedType, setSelectedType] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'timestamp' | 'confidence' | 'type'>('timestamp');

  const filteredResults = results.filter(result => 
    selectedType === 'all' || result.type === selectedType
  ).sort((a, b) => {
    switch (sortBy) {
      case 'timestamp':
        return b.timestamp.getTime() - a.timestamp.getTime();
      case 'confidence':
        return b.confidence - a.confidence;
      case 'type':
        return a.type.localeCompare(b.type);
      default:
        return 0;
    }
  });

  const getResultIcon = (type: string) => {
    switch (type) {
      case 'chart':
        return <BarChart3 className="w-5 h-5 text-blue-600" />;
      case 'metric':
        return <Activity className="w-5 h-5 text-green-600" />;
      case 'insight':
        return <Zap className="w-5 h-5 text-yellow-600" />;
      case 'recommendation':
        return <Target className="w-5 h-5 text-purple-600" />;
      default:
        return <Info className="w-5 h-5 text-gray-600" />;
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-600 bg-green-100';
    if (confidence >= 0.6) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const renderMetricVisualization = (result: AnalysisResult) => {
    const { value, trend, previousValue, unit } = result.data;
    const change = previousValue ? ((value - previousValue) / previousValue) * 100 : 0;
    const isPositive = change > 0;

    return (
      <div className="flex items-center justify-between p-4">
        <div>
          <div className="text-2xl font-bold text-gray-900">
            {typeof value === 'number' ? value.toLocaleString() : value}
            {unit && <span className="text-sm text-gray-500 ml-1">{unit}</span>}
          </div>
          {previousValue && (
            <div className={`flex items-center gap-1 text-sm ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
              {isPositive ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
              {Math.abs(change).toFixed(1)}% from previous
            </div>
          )}
        </div>
        <div className="text-right">
          <div className="w-16 h-16 bg-gray-100 rounded-lg flex items-center justify-center">
            {getResultIcon(result.type)}
          </div>
        </div>
      </div>
    );
  };

  const renderChartVisualization = (result: AnalysisResult) => {
    const { chartType, data } = result.data;
    
    return (
      <div className="p-4">
        <div className="h-32 bg-gray-50 rounded-lg flex items-center justify-center">
          <div className="text-center text-gray-500">
            <BarChart3 className="w-8 h-8 mx-auto mb-2" />
            <div className="text-sm">
              {chartType || 'Chart'} visualization
              {data?.length && <div className="text-xs">({data.length} data points)</div>}
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderInsightVisualization = (result: AnalysisResult) => {
    const { insights, priority } = result.data;
    
    return (
      <div className="p-4">
        <div className="space-y-2">
          {insights?.slice(0, 3).map((insight: string, index: number) => (
            <div key={index} className="flex items-start gap-2 text-sm">
              <div className={`w-2 h-2 rounded-full mt-2 ${
                priority === 'high' ? 'bg-red-500' :
                priority === 'medium' ? 'bg-yellow-500' : 'bg-green-500'
              }`} />
              <span className="text-gray-700">{insight}</span>
            </div>
          )) || (
            <div className="text-gray-500 text-sm">No insights available</div>
          )}
        </div>
      </div>
    );
  };

  const renderRecommendationVisualization = (result: AnalysisResult) => {
    const { recommendations, impact } = result.data;
    
    return (
      <div className="p-4">
        <div className="space-y-3">
          {recommendations?.slice(0, 2).map((rec: any, index: number) => (
            <div key={index} className="flex items-start gap-3">
              <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
              <div>
                <div className="text-sm font-medium text-gray-900">{rec.title}</div>
                <div className="text-xs text-gray-600">{rec.description}</div>
                {rec.impact && (
                  <div className="text-xs text-blue-600 mt-1">Impact: {rec.impact}</div>
                )}
              </div>
            </div>
          )) || (
            <div className="text-gray-500 text-sm">No recommendations available</div>
          )}
        </div>
      </div>
    );
  };

  const renderVisualization = (result: AnalysisResult) => {
    switch (result.type) {
      case 'metric':
        return renderMetricVisualization(result);
      case 'chart':
        return renderChartVisualization(result);
      case 'insight':
        return renderInsightVisualization(result);
      case 'recommendation':
        return renderRecommendationVisualization(result);
      default:
        return (
          <div className="p-4 text-center text-gray-500">
            <Info className="w-8 h-8 mx-auto mb-2" />
            <div className="text-sm">No visualization available</div>
          </div>
        );
    }
  };

  if (results.length === 0) {
    return (
      <div className={`flex flex-col items-center justify-center py-12 text-gray-500 ${className}`}>
        <Activity className="w-12 h-12 mb-4 text-gray-300" />
        <h3 className="text-lg font-medium mb-2">No results yet</h3>
        <p className="text-sm text-center max-w-md">
          Run an analysis or query to see visualized results and insights here.
        </p>
      </div>
    );
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Filters and Controls */}
      <div className="flex flex-wrap items-center justify-between gap-4 p-4 bg-gray-50 rounded-lg">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-gray-500" />
            <select
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value)}
              className="text-sm border border-gray-300 rounded px-2 py-1 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">All Types</option>
              <option value="chart">Charts</option>
              <option value="metric">Metrics</option>
              <option value="insight">Insights</option>
              <option value="recommendation">Recommendations</option>
            </select>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-500">Sort by:</span>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as any)}
              className="text-sm border border-gray-300 rounded px-2 py-1 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="timestamp">Latest</option>
              <option value="confidence">Confidence</option>
              <option value="type">Type</option>
            </select>
          </div>
        </div>

        <div className="flex items-center gap-2 text-sm text-gray-600">
          <span>{filteredResults.length} results</span>
        </div>
      </div>

      {/* Results Grid/List */}
      <div className={
        layout === 'grid' 
          ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'
          : 'space-y-4'
      }>
        {filteredResults.map((result) => (
          <div
            key={result.id}
            className="bg-white border border-gray-200 rounded-lg hover:shadow-lg transition-shadow duration-200 cursor-pointer"
            onClick={() => onResultSelect?.(result)}
          >
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-gray-100">
              <div className="flex items-center gap-3">
                {getResultIcon(result.type)}
                <div>
                  <h3 className="font-medium text-gray-900 truncate">{result.title}</h3>
                  <p className="text-sm text-gray-500 truncate">{result.description}</p>
                </div>
              </div>
              
              <div className="flex items-center gap-2">
                <div className={`px-2 py-1 rounded-full text-xs font-medium ${getConfidenceColor(result.confidence)}`}>
                  {Math.round(result.confidence * 100)}%
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onExport?.(result);
                  }}
                  className="p-1 hover:bg-gray-100 rounded transition-colors"
                  title="Export result"
                >
                  <Download className="w-4 h-4 text-gray-400" />
                </button>
              </div>
            </div>

            {/* Visualization */}
            <div className="min-h-[120px]">
              {renderVisualization(result)}
            </div>

            {/* Footer */}
            <div className="flex items-center justify-between p-4 bg-gray-50 text-xs text-gray-500">
              <div className="flex items-center gap-2">
                {result.metadata?.agentType && (
                  <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded">
                    {result.metadata.agentType}
                  </span>
                )}
                {result.metadata?.dataSource && (
                  <span>From: {result.metadata.dataSource}</span>
                )}
              </div>
              <div>
                {result.timestamp.toLocaleDateString()} {result.timestamp.toLocaleTimeString()}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export type { AnalysisResult };
