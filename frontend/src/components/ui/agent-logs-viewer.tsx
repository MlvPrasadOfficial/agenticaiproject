'use client';

import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FileText, 
  Download, 
  Search, 
  Filter, 
  RefreshCw, 
  Trash2, 
  Eye, 
  EyeOff, 
  ChevronDown,
  AlertCircle,
  Info,
  AlertTriangle,
  CheckCircle,
  Zap,
  Clock,
  Copy,
  ExternalLink
} from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

interface LogEntry {
  id: string;
  timestamp: Date;
  level: 'debug' | 'info' | 'warn' | 'error' | 'trace';
  agentId: string;
  agentName: string;
  category: string;
  message: string;
  details?: any;
  stackTrace?: string;
  metadata?: {
    requestId?: string;
    sessionId?: string;
    userId?: string;
    duration?: number;
    memoryUsage?: number;
    cpuUsage?: number;
  };
  tags?: string[];
}

interface LogFilter {
  level: string[];
  agents: string[];
  categories: string[];
  timeRange: 'last-hour' | 'last-day' | 'last-week' | 'custom';
  search: string;
  dateFrom?: Date;
  dateTo?: Date;
}

interface AgentLogsViewerProps {
  logs: LogEntry[];
  agents: Array<{ id: string; name: string }>;
  onRefresh?: () => void;
  onClearLogs?: () => void;
  onExportLogs?: (logs: LogEntry[]) => void;
  className?: string;
  autoRefresh?: boolean;
  refreshInterval?: number;
  maxLogs?: number;
}

export function AgentLogsViewer({
  logs,
  agents,
  onRefresh,
  onClearLogs,
  onExportLogs,
  className = '',
  autoRefresh = false,
  refreshInterval = 5000,
  maxLogs = 1000
}: AgentLogsViewerProps) {
  const [filter, setFilter] = useState<LogFilter>({
    level: [],
    agents: [],
    categories: [],
    timeRange: 'last-day',
    search: ''
  });
  const [selectedLog, setSelectedLog] = useState<LogEntry | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [showDetails, setShowDetails] = useState<Record<string, boolean>>({});
  const [viewMode, setViewMode] = useState<'compact' | 'detailed' | 'raw'>('compact');
  const logsEndRef = useRef<HTMLDivElement>(null);
  const searchInputRef = useRef<HTMLInputElement>(null);

  // Auto-refresh logs
  useEffect(() => {
    if (autoRefresh && refreshInterval > 0) {
      const interval = setInterval(() => {
        onRefresh?.();
      }, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [autoRefresh, refreshInterval, onRefresh]);

  // Auto-scroll to bottom for new logs
  useEffect(() => {
    if (viewMode !== 'raw') {
      logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs, viewMode]);

  // Filter logs based on current filter settings
  const filteredLogs = logs.filter(log => {
    // Level filter
    if (filter.level.length > 0 && !filter.level.includes(log.level)) {
      return false;
    }

    // Agent filter
    if (filter.agents.length > 0 && !filter.agents.includes(log.agentId)) {
      return false;
    }

    // Category filter
    if (filter.categories.length > 0 && !filter.categories.includes(log.category)) {
      return false;
    }

    // Search filter
    if (filter.search) {
      const searchLower = filter.search.toLowerCase();
      if (!log.message.toLowerCase().includes(searchLower) &&
          !log.category.toLowerCase().includes(searchLower) &&
          !log.agentName.toLowerCase().includes(searchLower)) {
        return false;
      }
    }

    // Time range filter
    const now = new Date();
    const logTime = log.timestamp;
    switch (filter.timeRange) {
      case 'last-hour':
        return now.getTime() - logTime.getTime() <= 60 * 60 * 1000;
      case 'last-day':
        return now.getTime() - logTime.getTime() <= 24 * 60 * 60 * 1000;
      case 'last-week':
        return now.getTime() - logTime.getTime() <= 7 * 24 * 60 * 60 * 1000;
      case 'custom':
        if (filter.dateFrom && logTime < filter.dateFrom) return false;
        if (filter.dateTo && logTime > filter.dateTo) return false;
        return true;
      default:
        return true;
    }
  }).slice(-maxLogs);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    onRefresh?.();
    setTimeout(() => setIsRefreshing(false), 1000);
  };

  const toggleLogDetails = (logId: string) => {
    setShowDetails(prev => ({
      ...prev,
      [logId]: !prev[logId]
    }));
  };

  const copyLogToClipboard = (log: LogEntry) => {
    const logText = `[${log.timestamp.toISOString()}] ${log.level.toUpperCase()} ${log.agentName} - ${log.message}`;
    navigator.clipboard.writeText(logText);
  };

  const getLevelIcon = (level: LogEntry['level']) => {
    switch (level) {
      case 'debug':
        return <FileText className="w-4 h-4 text-gray-500" />;
      case 'info':
        return <Info className="w-4 h-4 text-blue-500" />;
      case 'warn':
        return <AlertTriangle className="w-4 h-4 text-yellow-500" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      case 'trace':
        return <Zap className="w-4 h-4 text-purple-500" />;
      default:
        return <FileText className="w-4 h-4 text-gray-500" />;
    }
  };

  const getLevelColor = (level: LogEntry['level']) => {
    switch (level) {
      case 'debug':
        return 'text-gray-600 bg-gray-100 dark:bg-gray-800 dark:text-gray-400';
      case 'info':
        return 'text-blue-600 bg-blue-100 dark:bg-blue-900/20 dark:text-blue-400';
      case 'warn':
        return 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900/20 dark:text-yellow-400';
      case 'error':
        return 'text-red-600 bg-red-100 dark:bg-red-900/20 dark:text-red-400';
      case 'trace':
        return 'text-purple-600 bg-purple-100 dark:bg-purple-900/20 dark:text-purple-400';
      default:
        return 'text-gray-600 bg-gray-100 dark:bg-gray-800 dark:text-gray-400';
    }
  };

  const renderLogEntry = (log: LogEntry, index: number) => {
    const isExpanded = showDetails[log.id];

    return (
      <motion.div
        key={log.id}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: index * 0.02 }}
        className={`
          border-l-4 pl-4 pr-2 py-2 hover:bg-gray-50 dark:hover:bg-gray-800/50
          ${getLevelColor(log.level).includes('text-red') ? 'border-red-500' :
            getLevelColor(log.level).includes('text-yellow') ? 'border-yellow-500' :
            getLevelColor(log.level).includes('text-blue') ? 'border-blue-500' :
            getLevelColor(log.level).includes('text-purple') ? 'border-purple-500' :
            'border-gray-300'
          }
        `}
      >
        <div className="flex items-start gap-3">
          {/* Level Icon */}
          <div className="flex-shrink-0 mt-0.5">
            {getLevelIcon(log.level)}
          </div>

          {/* Main Content */}
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                {/* Header */}
                <div className="flex items-center gap-2 mb-1">
                  <span className={`
                    px-2 py-1 rounded text-xs font-medium uppercase
                    ${getLevelColor(log.level)}
                  `}>
                    {log.level}
                  </span>
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    {log.agentName}
                  </span>
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    {log.category}
                  </span>
                  <span className="text-xs text-gray-400">
                    {formatDistanceToNow(log.timestamp, { addSuffix: true })}
                  </span>
                </div>

                {/* Message */}
                <div className="text-sm text-gray-800 dark:text-gray-200 mb-2">
                  <pre className="whitespace-pre-wrap font-mono text-xs">
                    {log.message}
                  </pre>
                </div>

                {/* Tags */}
                {log.tags && log.tags.length > 0 && (
                  <div className="flex flex-wrap gap-1 mb-2">
                    {log.tags.map(tag => (
                      <span
                        key={tag}
                        className="px-1.5 py-0.5 bg-gray-200 dark:bg-gray-700 text-xs rounded"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                )}

                {/* Metadata */}
                {log.metadata && (
                  <div className="flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400">
                    {log.metadata.requestId && (
                      <span>ID: {log.metadata.requestId.slice(0, 8)}</span>
                    )}
                    {log.metadata.duration && (
                      <span>Duration: {log.metadata.duration}ms</span>
                    )}
                    {log.metadata.memoryUsage && (
                      <span>Memory: {log.metadata.memoryUsage}MB</span>
                    )}
                  </div>
                )}
              </div>

              {/* Actions */}
              <div className="flex items-center gap-1 ml-2 opacity-0 group-hover:opacity-100 transition-opacity">
                <button
                  onClick={() => copyLogToClipboard(log)}
                  className="p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-700"
                  title="Copy log"
                >
                  <Copy className="w-3 h-3" />
                </button>
                <button
                  onClick={() => setSelectedLog(log)}
                  className="p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-700"
                  title="View details"
                >
                  <ExternalLink className="w-3 h-3" />
                </button>
                {(log.details || log.stackTrace) && (
                  <button
                    onClick={() => toggleLogDetails(log.id)}
                    className="p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-700"
                    title="Toggle details"
                  >
                    <ChevronDown className={`w-3 h-3 transition-transform ${isExpanded ? 'rotate-180' : ''}`} />
                  </button>
                )}
              </div>
            </div>

            {/* Expanded Details */}
            <AnimatePresence>
              {isExpanded && (log.details || log.stackTrace) && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  className="mt-2 p-3 bg-gray-100 dark:bg-gray-800 rounded text-xs overflow-hidden"
                >
                  {log.details && (
                    <div className="mb-2">
                      <h5 className="font-medium mb-1">Details:</h5>
                      <pre className="whitespace-pre-wrap font-mono text-xs text-gray-600 dark:text-gray-400">
                        {typeof log.details === 'string' ? log.details : JSON.stringify(log.details, null, 2)}
                      </pre>
                    </div>
                  )}
                  {log.stackTrace && (
                    <div>
                      <h5 className="font-medium mb-1">Stack Trace:</h5>
                      <pre className="whitespace-pre-wrap font-mono text-xs text-red-600 dark:text-red-400">
                        {log.stackTrace}
                      </pre>
                    </div>
                  )}
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </motion.div>
    );
  };

  const renderFilters = () => (
    <AnimatePresence>
      {showFilters && (
        <motion.div
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: 'auto', opacity: 1 }}
          exit={{ height: 0, opacity: 0 }}
          className="p-4 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50"
        >
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Level Filter */}
            <div>
              <label className="block text-sm font-medium mb-2">Log Level</label>
              <div className="space-y-1">
                {['debug', 'info', 'warn', 'error', 'trace'].map(level => (
                  <label key={level} className="flex items-center">
                    <input
                      type="checkbox"
                      checked={filter.level.includes(level)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setFilter(prev => ({ ...prev, level: [...prev.level, level] }));
                        } else {
                          setFilter(prev => ({ ...prev, level: prev.level.filter(l => l !== level) }));
                        }
                      }}
                      className="mr-2"
                    />
                    <span className="text-sm capitalize">{level}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Agent Filter */}
            <div>
              <label className="block text-sm font-medium mb-2">Agents</label>
              <div className="space-y-1 max-h-32 overflow-y-auto">
                {agents.map(agent => (
                  <label key={agent.id} className="flex items-center">
                    <input
                      type="checkbox"
                      checked={filter.agents.includes(agent.id)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setFilter(prev => ({ ...prev, agents: [...prev.agents, agent.id] }));
                        } else {
                          setFilter(prev => ({ ...prev, agents: prev.agents.filter(a => a !== agent.id) }));
                        }
                      }}
                      className="mr-2"
                    />
                    <span className="text-sm">{agent.name}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Time Range */}
            <div>
              <label className="block text-sm font-medium mb-2">Time Range</label>
              <select
                value={filter.timeRange}
                onChange={(e) => setFilter(prev => ({ ...prev, timeRange: e.target.value as any }))}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded text-sm"
              >
                <option value="last-hour">Last Hour</option>
                <option value="last-day">Last 24 Hours</option>
                <option value="last-week">Last Week</option>
                <option value="custom">Custom Range</option>
              </select>
            </div>

            {/* Actions */}
            <div className="flex flex-col gap-2">
              <button
                onClick={() => setFilter({
                  level: [],
                  agents: [],
                  categories: [],
                  timeRange: 'last-day',
                  search: ''
                })}
                className="px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded hover:bg-gray-100 dark:hover:bg-gray-700"
              >
                Clear Filters
              </button>
              <button
                onClick={() => onExportLogs?.(filteredLogs)}
                className="px-3 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                Export Logs
              </button>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );

  return (
    <div className={`flex flex-col h-full ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center gap-2">
          <FileText className="w-5 h-5 text-blue-600" />
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
            Agent Logs
          </h2>
          <span className="px-2 py-1 bg-gray-100 dark:bg-gray-800 text-xs rounded">
            {filteredLogs.length} entries
          </span>
        </div>

        <div className="flex items-center gap-2">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              ref={searchInputRef}
              type="text"
              placeholder="Search logs..."
              value={filter.search}
              onChange={(e) => setFilter(prev => ({ ...prev, search: e.target.value }))}
              className="pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm w-64"
            />
          </div>

          {/* View Mode */}
          <select
            value={viewMode}
            onChange={(e) => setViewMode(e.target.value as any)}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded text-sm"
          >
            <option value="compact">Compact</option>
            <option value="detailed">Detailed</option>
            <option value="raw">Raw</option>
          </select>

          {/* Filter Toggle */}
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`p-2 rounded ${showFilters ? 'bg-blue-100 text-blue-600' : 'hover:bg-gray-100 dark:hover:bg-gray-700'}`}
          >
            <Filter className="w-4 h-4" />
          </button>

          {/* Refresh */}
          <button
            onClick={handleRefresh}
            disabled={isRefreshing}
            className="p-2 rounded hover:bg-gray-100 dark:hover:bg-gray-700"
          >
            <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
          </button>

          {/* Clear */}
          <button
            onClick={onClearLogs}
            className="p-2 rounded hover:bg-gray-100 dark:hover:bg-gray-700 text-red-600"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Filters */}
      {renderFilters()}

      {/* Logs Container */}
      <div className="flex-1 overflow-y-auto">
        <div className="p-2 space-y-1">
          {filteredLogs.length === 0 ? (
            <div className="flex items-center justify-center h-32 text-gray-500 dark:text-gray-400">
              <div className="text-center">
                <FileText className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p>No logs match the current filters</p>
              </div>
            </div>
          ) : (
            <div className="group">
              {filteredLogs.map((log, index) => renderLogEntry(log, index))}
            </div>
          )}
          <div ref={logsEndRef} />
        </div>
      </div>

      {/* Log Detail Modal */}
      <AnimatePresence>
        {selectedLog && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
            onClick={() => setSelectedLog(null)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Log Details</h3>
                <button
                  onClick={() => setSelectedLog(null)}
                  className="text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
                >
                  ×
                </button>
              </div>
              
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="font-medium">Level:</span> {selectedLog.level}
                  </div>
                  <div>
                    <span className="font-medium">Agent:</span> {selectedLog.agentName}
                  </div>
                  <div>
                    <span className="font-medium">Category:</span> {selectedLog.category}
                  </div>
                  <div>
                    <span className="font-medium">Time:</span> {selectedLog.timestamp.toLocaleString()}
                  </div>
                </div>
                
                <div>
                  <span className="font-medium">Message:</span>
                  <pre className="mt-2 p-3 bg-gray-100 dark:bg-gray-700 rounded text-sm whitespace-pre-wrap">
                    {selectedLog.message}
                  </pre>
                </div>
                
                {selectedLog.details && (
                  <div>
                    <span className="font-medium">Details:</span>
                    <pre className="mt-2 p-3 bg-gray-100 dark:bg-gray-700 rounded text-sm whitespace-pre-wrap">
                      {typeof selectedLog.details === 'string' ? selectedLog.details : JSON.stringify(selectedLog.details, null, 2)}
                    </pre>
                  </div>
                )}
                
                {selectedLog.stackTrace && (
                  <div>
                    <span className="font-medium">Stack Trace:</span>
                    <pre className="mt-2 p-3 bg-red-100 dark:bg-red-900/20 rounded text-sm whitespace-pre-wrap text-red-800 dark:text-red-400">
                      {selectedLog.stackTrace}
                    </pre>
                  </div>
                )}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
