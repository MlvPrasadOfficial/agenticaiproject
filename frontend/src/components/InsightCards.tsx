'use client';

import React, { useState } from 'react';
import { 
  Lightbulb, 
  TrendingUp, 
  TrendingDown, 
  AlertTriangle, 
  CheckCircle, 
  Info,
  ArrowRight,
  Star,
  Clock,
  Target,
  Zap,
  BookOpen,
  Eye,
  EyeOff,
  Pin,
  X
} from 'lucide-react';

interface Insight {
  id: string;
  type: 'trend' | 'anomaly' | 'opportunity' | 'risk' | 'success' | 'info';
  title: string;
  description: string;
  impact: 'high' | 'medium' | 'low';
  confidence: number;
  priority: number;
  timestamp: Date;
  data?: {
    value?: number;
    change?: number;
    trend?: 'up' | 'down' | 'stable';
    context?: string;
    recommendations?: string[];
  };
  tags?: string[];
  isPinned?: boolean;
  isRead?: boolean;
}

interface InsightCardsProps {
  insights: Insight[];
  onInsightClick?: (insight: Insight) => void;
  onInsightPin?: (insightId: string) => void;
  onInsightDismiss?: (insightId: string) => void;
  onInsightMarkRead?: (insightId: string) => void;
  className?: string;
  maxCards?: number;
  showFilters?: boolean;
}

export default function InsightCards({
  insights,
  onInsightClick,
  onInsightPin,
  onInsightDismiss,
  onInsightMarkRead,
  className = '',
  maxCards = 6,
  showFilters = true
}: InsightCardsProps) {
  const [filter, setFilter] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'priority' | 'timestamp' | 'impact'>('priority');
  const [showOnlyUnread, setShowOnlyUnread] = useState(false);

  const getInsightIcon = (type: string) => {
    switch (type) {
      case 'trend':
        return <TrendingUp className="w-5 h-5" />;
      case 'anomaly':
        return <AlertTriangle className="w-5 h-5" />;
      case 'opportunity':
        return <Target className="w-5 h-5" />;
      case 'risk':
        return <AlertTriangle className="w-5 h-5" />;
      case 'success':
        return <CheckCircle className="w-5 h-5" />;
      case 'info':
      default:
        return <Info className="w-5 h-5" />;
    }
  };

  const getInsightColor = (type: string) => {
    switch (type) {
      case 'trend':
        return 'text-blue-600 bg-blue-100 border-blue-200';
      case 'anomaly':
        return 'text-orange-600 bg-orange-100 border-orange-200';
      case 'opportunity':
        return 'text-green-600 bg-green-100 border-green-200';
      case 'risk':
        return 'text-red-600 bg-red-100 border-red-200';
      case 'success':
        return 'text-emerald-600 bg-emerald-100 border-emerald-200';
      case 'info':
      default:
        return 'text-gray-600 bg-gray-100 border-gray-200';
    }
  };

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'high':
        return 'bg-red-500 text-white';
      case 'medium':
        return 'bg-yellow-500 text-white';
      case 'low':
        return 'bg-green-500 text-white';
      default:
        return 'bg-gray-500 text-white';
    }
  };

  const filteredInsights = insights
    .filter(insight => {
      if (filter !== 'all' && insight.type !== filter) return false;
      if (showOnlyUnread && insight.isRead) return false;
      return true;
    })
    .sort((a, b) => {
      // Pinned insights first
      if (a.isPinned && !b.isPinned) return -1;
      if (!a.isPinned && b.isPinned) return 1;

      switch (sortBy) {
        case 'priority':
          return b.priority - a.priority;
        case 'timestamp':
          return b.timestamp.getTime() - a.timestamp.getTime();
        case 'impact':
          const impactOrder = { high: 3, medium: 2, low: 1 };
          return (impactOrder[b.impact] || 0) - (impactOrder[a.impact] || 0);
        default:
          return 0;
      }
    })
    .slice(0, maxCards);

  const formatTimeAgo = (date: Date) => {
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffHours / 24);

    if (diffDays > 0) return `${diffDays}d ago`;
    if (diffHours > 0) return `${diffHours}h ago`;
    return 'Just now';
  };

  if (insights.length === 0) {
    return (
      <div className={`flex flex-col items-center justify-center py-12 text-gray-500 ${className}`}>
        <Lightbulb className="w-12 h-12 mb-4 text-gray-300" />
        <h3 className="text-lg font-medium mb-2">No insights yet</h3>
        <p className="text-sm text-center max-w-md">
          Insights will appear here as data is analyzed and patterns are discovered.
        </p>
      </div>
    );
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Summary */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-6">
        <div className="flex items-center gap-3 mb-4">
          <Lightbulb className="w-6 h-6 text-blue-600" />
          <h2 className="text-xl font-semibold text-gray-900">Insights Summary</h2>
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">{insights.length}</div>
            <div className="text-sm text-gray-600">Total Insights</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-red-600">
              {insights.filter(i => i.impact === 'high').length}
            </div>
            <div className="text-sm text-gray-600">High Impact</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-orange-600">
              {insights.filter(i => !i.isRead).length}
            </div>
            <div className="text-sm text-gray-600">Unread</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">
              {insights.filter(i => i.isPinned).length}
            </div>
            <div className="text-sm text-gray-600">Pinned</div>
          </div>
        </div>
      </div>

      {/* Filters */}
      {showFilters && (
        <div className="flex flex-wrap items-center gap-4 p-4 bg-gray-50 rounded-lg">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-gray-700">Filter:</span>
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="text-sm border border-gray-300 rounded px-2 py-1 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">All Types</option>
              <option value="trend">Trends</option>
              <option value="anomaly">Anomalies</option>
              <option value="opportunity">Opportunities</option>
              <option value="risk">Risks</option>
              <option value="success">Successes</option>
              <option value="info">Information</option>
            </select>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-gray-700">Sort:</span>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as any)}
              className="text-sm border border-gray-300 rounded px-2 py-1 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="priority">Priority</option>
              <option value="timestamp">Recent</option>
              <option value="impact">Impact</option>
            </select>
          </div>

          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={showOnlyUnread}
              onChange={(e) => setShowOnlyUnread(e.target.checked)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="text-sm text-gray-700">Unread only</span>
          </label>
        </div>
      )}

      {/* Insight Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredInsights.map((insight) => (
          <div
            key={insight.id}
            className={`
              relative bg-white border rounded-lg hover:shadow-lg transition-all duration-200 cursor-pointer
              ${getInsightColor(insight.type)}
              ${!insight.isRead ? 'ring-2 ring-blue-200' : ''}
              ${insight.isPinned ? 'ring-2 ring-yellow-300' : ''}
            `}
            onClick={() => {
              onInsightClick?.(insight);
              onInsightMarkRead?.(insight.id);
            }}
          >
            {/* Header */}
            <div className="p-4 border-b border-gray-100">
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  {getInsightIcon(insight.type)}
                  <span className={`px-2 py-1 rounded text-xs font-medium ${getImpactColor(insight.impact)}`}>
                    {insight.impact.toUpperCase()}
                  </span>
                </div>
                
                <div className="flex items-center gap-1">
                  {insight.isPinned && (
                    <Pin className="w-4 h-4 text-yellow-500" />
                  )}
                  {!insight.isRead && (
                    <div className="w-2 h-2 bg-blue-500 rounded-full" />
                  )}
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onInsightDismiss?.(insight.id);
                    }}
                    className="p-1 hover:bg-gray-100 rounded transition-colors"
                    title="Dismiss"
                  >
                    <X className="w-3 h-3 text-gray-400" />
                  </button>
                </div>
              </div>

              <h3 className="font-semibold text-gray-900 mb-1">{insight.title}</h3>
              <p className="text-sm text-gray-600 line-clamp-2">{insight.description}</p>
            </div>

            {/* Content */}
            <div className="p-4">
              {insight.data && (
                <div className="space-y-3">
                  {insight.data.value && (
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-500">Value:</span>
                      <span className="font-medium">{insight.data.value.toLocaleString()}</span>
                    </div>
                  )}
                  
                  {insight.data.change && (
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-500">Change:</span>
                      <div className={`flex items-center gap-1 ${
                        insight.data.change > 0 ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {insight.data.change > 0 ? (
                          <TrendingUp className="w-4 h-4" />
                        ) : (
                          <TrendingDown className="w-4 h-4" />
                        )}
                        <span className="font-medium">{Math.abs(insight.data.change)}%</span>
                      </div>
                    </div>
                  )}

                  {insight.data.recommendations && insight.data.recommendations.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-gray-100">
                      <div className="text-sm font-medium text-gray-700 mb-2">Recommendations:</div>
                      <ul className="space-y-1">
                        {insight.data.recommendations.slice(0, 2).map((rec, index) => (
                          <li key={index} className="flex items-start gap-2 text-sm text-gray-600">
                            <ArrowRight className="w-3 h-3 mt-0.5 text-blue-500 flex-shrink-0" />
                            <span>{rec}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}

              {insight.tags && insight.tags.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-3">
                  {insight.tags.slice(0, 3).map((tag, index) => (
                    <span
                      key={index}
                      className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="flex items-center justify-between p-4 bg-gray-50 border-t border-gray-100">
              <div className="flex items-center gap-2 text-xs text-gray-500">
                <Clock className="w-3 h-3" />
                <span>{formatTimeAgo(insight.timestamp)}</span>
              </div>
              
              <div className="flex items-center gap-2">
                <div className="flex items-center gap-1 text-xs text-gray-500">
                  <Star className="w-3 h-3" />
                  <span>{Math.round(insight.confidence * 100)}%</span>
                </div>
                
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onInsightPin?.(insight.id);
                  }}
                  className={`p-1 rounded transition-colors ${
                    insight.isPinned ? 'text-yellow-500 hover:text-yellow-600' : 'text-gray-400 hover:text-gray-600'
                  }`}
                  title={insight.isPinned ? 'Unpin' : 'Pin'}
                >
                  <Pin className="w-3 h-3" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {filteredInsights.length === 0 && insights.length > 0 && (
        <div className="text-center py-8 text-gray-500">
          <Info className="w-8 h-8 mx-auto mb-2" />
          <p>No insights match the current filters.</p>
        </div>
      )}
    </div>
  );
}

export type { Insight };
