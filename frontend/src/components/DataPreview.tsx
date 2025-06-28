'use client';

import { FileText, TrendingUp, AlertTriangle, CheckCircle, BarChart3, Database } from 'lucide-react';
import { DataPreviewResponse, DataStatisticsResponse } from '../services/api';

interface DataPreviewProps {
  preview: DataPreviewResponse;
  statistics: DataStatisticsResponse;
  isLoading?: boolean;
}

export default function DataPreview({ preview, statistics, isLoading = false }: DataPreviewProps) {
  if (isLoading) {
    return (
      <div className="card-glass p-6 animate-pulse">
        <div className="h-6 bg-glass-hover rounded mb-4"></div>
        <div className="space-y-3">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-4 bg-glass-hover rounded"></div>
          ))}
        </div>
      </div>
    );
  }

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat().format(num);
  };

  const getQualityColor = (score: number) => {
    if (score >= 0.8) return 'text-accent-tertiary';
    if (score >= 0.6) return 'text-yellow-400';
    return 'text-accent-error';
  };

  const getQualityIcon = (score: number) => {
    if (score >= 0.8) return <CheckCircle className="w-4 h-4" />;
    if (score >= 0.6) return <AlertTriangle className="w-4 h-4" />;
    return <AlertTriangle className="w-4 h-4" />;
  };

  return (
    <div className="space-y-6">
      {/* File Overview */}
      <div className="card-glass p-6">
        <h3 className="text-xl font-bold text-text-primary mb-4 flex items-center gap-3">
          <FileText className="w-5 h-5 text-accent-primary" />
          Data Overview
        </h3>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-glass-bg p-4 rounded-lg border border-glass-border">
            <div className="flex items-center gap-2 mb-2">
              <Database className="w-4 h-4 text-accent-secondary" />
              <span className="text-sm text-text-muted">Rows</span>
            </div>
            <div className="text-2xl font-bold text-text-primary">
              {formatNumber(preview.total_rows)}
            </div>
          </div>
          
          <div className="bg-glass-bg p-4 rounded-lg border border-glass-border">
            <div className="flex items-center gap-2 mb-2">
              <BarChart3 className="w-4 h-4 text-accent-tertiary" />
              <span className="text-sm text-text-muted">Columns</span>
            </div>
            <div className="text-2xl font-bold text-text-primary">
              {preview.total_columns}
            </div>
          </div>
          
          <div className="bg-glass-bg p-4 rounded-lg border border-glass-border">
            <div className="flex items-center gap-2 mb-2">
              <TrendingUp className="w-4 h-4 text-accent-primary" />
              <span className="text-sm text-text-muted">Quality Score</span>
            </div>
            <div className={`text-2xl font-bold flex items-center gap-2 ${getQualityColor(statistics.overall_stats.data_quality_score)}`}>
              {getQualityIcon(statistics.overall_stats.data_quality_score)}
              {Math.round(statistics.overall_stats.data_quality_score * 100)}%
            </div>
          </div>
          
          <div className="bg-glass-bg p-4 rounded-lg border border-glass-border">
            <div className="flex items-center gap-2 mb-2">
              <Database className="w-4 h-4 text-text-muted" />
              <span className="text-sm text-text-muted">Memory</span>
            </div>
            <div className="text-2xl font-bold text-text-primary">
              {statistics.overall_stats.memory_usage_mb.toFixed(1)} MB
            </div>
          </div>
        </div>
      </div>

      {/* Data Quality Issues */}
      {statistics.data_quality.issues.length > 0 && (
        <div className="card-glass p-6">
          <h3 className="text-lg font-semibold text-text-primary mb-4 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-yellow-400" />
            Data Quality Issues
          </h3>
          <div className="space-y-2">
            {statistics.data_quality.issues.slice(0, 5).map((issue, index) => (
              <div key={index} className="flex items-start gap-2 p-3 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
                <AlertTriangle className="w-4 h-4 text-yellow-400 mt-0.5 flex-shrink-0" />
                <span className="text-sm text-text-secondary">{issue}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recommendations */}
      {statistics.recommendations.length > 0 && (
        <div className="card-glass p-6">
          <h3 className="text-lg font-semibold text-text-primary mb-4 flex items-center gap-2">
            <CheckCircle className="w-5 h-5 text-accent-tertiary" />
            Recommendations
          </h3>
          <div className="space-y-2">
            {statistics.recommendations.slice(0, 3).map((recommendation, index) => (
              <div key={index} className="flex items-start gap-2 p-3 bg-accent-tertiary/10 border border-accent-tertiary/20 rounded-lg">
                <CheckCircle className="w-4 h-4 text-accent-tertiary mt-0.5 flex-shrink-0" />
                <span className="text-sm text-text-secondary">{recommendation}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Data Preview Table */}
      <div className="card-glass p-6">
        <h3 className="text-lg font-semibold text-text-primary mb-4 flex items-center gap-2">
          <FileText className="w-5 h-5 text-accent-secondary" />
          Data Preview ({preview.preview_rows} of {formatNumber(preview.total_rows)} rows)
        </h3>
        
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-glass-border">
                {preview.columns.map((column, index) => (
                  <th key={index} className="text-left p-3 text-text-primary font-medium">
                    <div className="flex flex-col gap-1">
                      <span>{column.name}</span>
                      <span className="text-xs text-text-muted font-normal">
                        {column.type}
                        {column.null_percentage > 0 && (
                          <span className="ml-1 text-yellow-400">
                            ({column.null_percentage.toFixed(1)}% null)
                          </span>
                        )}
                      </span>
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {preview.data.map((row, rowIndex) => (
                <tr key={rowIndex} className="border-b border-glass-border/50 hover:bg-glass-hover/50">
                  {preview.columns.map((column, colIndex) => (
                    <td key={colIndex} className="p-3 text-text-secondary">
                      <div className="max-w-[200px] truncate">
                        {row[column.name] !== null && row[column.name] !== undefined 
                          ? String(row[column.name]) 
                          : <span className="text-text-muted italic">null</span>
                        }
                      </div>
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        {preview.has_more && (
          <div className="mt-4 text-center">
            <p className="text-sm text-text-muted">
              Showing first {preview.preview_rows} rows. Total: {formatNumber(preview.total_rows)} rows
            </p>
          </div>
        )}
      </div>

      {/* Column Statistics */}
      <div className="card-glass p-6">
        <h3 className="text-lg font-semibold text-text-primary mb-4 flex items-center gap-2">
          <BarChart3 className="w-5 h-5 text-accent-primary" />
          Column Statistics
        </h3>
        
        <div className="grid gap-4">
          {statistics.column_statistics.slice(0, 10).map((column, index) => (
            <div key={index} className="bg-glass-bg p-4 rounded-lg border border-glass-border">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium text-text-primary">{column.name}</h4>
                <div className={`flex items-center gap-1 ${getQualityColor(column.quality_score)}`}>
                  {getQualityIcon(column.quality_score)}
                  <span className="text-sm font-medium">
                    {Math.round(column.quality_score * 100)}%
                  </span>
                </div>
              </div>
              <div className="text-sm text-text-muted mb-2">
                Type: <span className="text-accent-secondary">{column.type}</span>
              </div>
              {column.issues.length > 0 && (
                <div className="text-xs text-yellow-400">
                  Issues: {column.issues.join(', ')}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
