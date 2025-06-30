'use client';

import React, { useState, useEffect, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Activity, 
  Clock, 
  Zap, 
  TrendingUp, 
  BarChart3, 
  PieChart, 
  Target,
  CheckCircle,
  Cpu,
  HardDrive
} from 'lucide-react';

interface AgentMetrics {
  agentId: string;
  agentName: string;
  status: 'active' | 'idle' | 'error' | 'offline';
  performance: {
    tasksCompleted: number;
    averageExecutionTime: number;
    successRate: number;
    tokensProcessed: number;
    memoryUsage: number;
    cpuUsage: number;
  };
  historicalData: {
    timestamp: Date;
    executionTime: number;
    success: boolean;
    tokensUsed: number;
  }[];
  lastActivity: Date;
}

interface AgentPerformanceMetricsProps {
  agents: AgentMetrics[];
  refreshInterval?: number;
  className?: string;
  onAgentSelect?: (agentId: string) => void;
  selectedAgentId?: string;
  showComparison?: boolean;
}

export function AgentPerformanceMetrics({
  agents,
  refreshInterval = 5000,
  className = '',
  onAgentSelect,
  selectedAgentId,
  showComparison = false
}: Readonly<AgentPerformanceMetricsProps>) {
  const [viewMode, setViewMode] = useState<'grid' | 'list' | 'comparison'>('grid');
  const [sortBy, setSortBy] = useState<'name' | 'performance' | 'activity'>('performance');

  // Auto-refresh simulation
  useEffect(() => {
    if (refreshInterval > 0) {
      const interval = setInterval(() => {
        // Trigger re-render for animations
      }, refreshInterval);
      
      return () => clearInterval(interval);
    }
  }, [refreshInterval]);

  const sortedAgents = useMemo(() => {
    return [...agents].sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.agentName.localeCompare(b.agentName);
        case 'performance':
          return b.performance.successRate - a.performance.successRate;
        case 'activity':
          return b.lastActivity.getTime() - a.lastActivity.getTime();
        default:
          return 0;
      }
    });
  }, [agents, sortBy]);

  const getStatusColor = (status: AgentMetrics['status']) => {
    switch (status) {
      case 'active':
        return 'text-green-500 bg-green-100 dark:bg-green-900/20';
      case 'idle':
        return 'text-yellow-500 bg-yellow-100 dark:bg-yellow-900/20';
      case 'error':
        return 'text-red-500 bg-red-100 dark:bg-red-900/20';
      case 'offline':
        return 'text-gray-500 bg-gray-100 dark:bg-gray-900/20';
    }
  };

  const getPerformanceGrade = (successRate: number) => {
    if (successRate >= 95) return { grade: 'A+', color: 'text-green-600' };
    if (successRate >= 90) return { grade: 'A', color: 'text-green-500' };
    if (successRate >= 85) return { grade: 'B+', color: 'text-blue-500' };
    if (successRate >= 80) return { grade: 'B', color: 'text-blue-400' };
    if (successRate >= 75) return { grade: 'C+', color: 'text-yellow-500' };
    if (successRate >= 70) return { grade: 'C', color: 'text-yellow-600' };
    return { grade: 'D', color: 'text-red-500' };
  };

  const renderMetricCard = (agent: AgentMetrics, index: number) => {
    const isSelected = selectedAgentId === agent.agentId;
    const performanceGrade = getPerformanceGrade(agent.performance.successRate);

    return (
      <motion.div
        key={agent.agentId}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: index * 0.1 }}
        className={`
          bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700
          hover:border-blue-300 dark:hover:border-blue-600 transition-all duration-200
          cursor-pointer group relative overflow-hidden
          ${isSelected ? 'ring-2 ring-blue-500 border-blue-300 dark:border-blue-600' : ''}
        `}
        onClick={() => onAgentSelect?.(agent.agentId)}
        whileHover={{ scale: 1.02, y: -2 }}
      >
        {/* Header */}
        <div className="p-4 border-b border-gray-100 dark:border-gray-700">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-semibold text-gray-900 dark:text-gray-100">
              {agent.agentName}
            </h3>
            <div className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(agent.status)}`}>
              {agent.status}
            </div>
          </div>
          
          <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400">
            <span>ID: {agent.agentId}</span>
            <span>Last: {new Date(agent.lastActivity).toLocaleTimeString()}</span>
          </div>
        </div>

        {/* Performance Grade */}
        <div className="absolute top-4 right-16">
          <div className={`text-2xl font-bold ${performanceGrade.color}`}>
            {performanceGrade.grade}
          </div>
        </div>

        {/* Metrics Grid */}
        <div className="p-4 space-y-4">
          {/* Primary Metrics */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <Target className="w-4 h-4 text-blue-500" />
                <span className="text-sm text-gray-600 dark:text-gray-400">Success Rate</span>
              </div>
              <div className="text-xl font-bold text-gray-900 dark:text-gray-100">
                {agent.performance.successRate.toFixed(1)}%
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <motion.div
                  className="bg-blue-500 h-2 rounded-full"
                  initial={{ width: 0 }}
                  animate={{ width: `${agent.performance.successRate}%` }}
                  transition={{ duration: 1, delay: 0.5 }}
                />
              </div>
            </div>

            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4 text-green-500" />
                <span className="text-sm text-gray-600 dark:text-gray-400">Avg Time</span>
              </div>
              <div className="text-xl font-bold text-gray-900 dark:text-gray-100">
                {agent.performance.averageExecutionTime.toFixed(0)}ms
              </div>
              <div className="text-xs text-gray-500">
                {agent.performance.tasksCompleted} tasks
              </div>
            </div>
          </div>

          {/* Secondary Metrics */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <Cpu className="w-4 h-4 text-purple-500" />
                <span className="text-sm text-gray-600 dark:text-gray-400">CPU</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                  {agent.performance.cpuUsage.toFixed(1)}%
                </span>
                <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
                  <motion.div
                    className={`h-1.5 rounded-full ${
                      agent.performance.cpuUsage > 80 ? 'bg-red-500' :
                      agent.performance.cpuUsage > 60 ? 'bg-yellow-500' : 'bg-green-500'
                    }`}
                    initial={{ width: 0 }}
                    animate={{ width: `${agent.performance.cpuUsage}%` }}
                    transition={{ duration: 1, delay: 0.7 }}
                  />
                </div>
              </div>
            </div>

            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <HardDrive className="w-4 h-4 text-orange-500" />
                <span className="text-sm text-gray-600 dark:text-gray-400">Memory</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                  {agent.performance.memoryUsage.toFixed(1)}%
                </span>
                <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
                  <motion.div
                    className={`h-1.5 rounded-full ${
                      agent.performance.memoryUsage > 80 ? 'bg-red-500' :
                      agent.performance.memoryUsage > 60 ? 'bg-yellow-500' : 'bg-green-500'
                    }`}
                    initial={{ width: 0 }}
                    animate={{ width: `${agent.performance.memoryUsage}%` }}
                    transition={{ duration: 1, delay: 0.9 }}
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Token Usage */}
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <Zap className="w-4 h-4 text-yellow-500" />
              <span className="text-sm text-gray-600 dark:text-gray-400">Tokens Processed</span>
            </div>
            <div className="text-lg font-semibold text-gray-900 dark:text-gray-100">
              {agent.performance.tokensProcessed.toLocaleString()}
            </div>
          </div>

          {/* Mini Chart */}
          <div className="pt-2">
            <div className="text-xs text-gray-600 dark:text-gray-400 mb-2">Recent Performance</div>
            <div className="h-8 flex items-end justify-between gap-1">
              {agent.historicalData.slice(-10).map((data, idx) => (
                <motion.div
                  key={idx}
                  className={`flex-1 rounded-t ${
                    data.success ? 'bg-green-400' : 'bg-red-400'
                  }`}
                  initial={{ height: 0 }}
                  animate={{ height: `${(data.executionTime / 1000) * 32}px` }}
                  transition={{ duration: 0.5, delay: idx * 0.05 }}
                  style={{ maxHeight: '32px' }}
                />
              ))}
            </div>
          </div>
        </div>

        {/* Hover Overlay */}
        <div className="absolute inset-0 bg-blue-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none" />
      </motion.div>
    );
  };

  const renderComparisonView = () => {
    const metrics = ['successRate', 'averageExecutionTime', 'tokensProcessed', 'cpuUsage', 'memoryUsage'];
    
    return (
      <div className="space-y-6">
        {metrics.map((metric, index) => (
          <motion.div
            key={metric}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
            className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700"
          >
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4 capitalize">
              {metric.replace(/([A-Z])/g, ' $1').trim()}
            </h3>
            
            <div className="space-y-3">
              {sortedAgents.map((agent, agentIndex) => {
                const value = agent.performance[metric as keyof typeof agent.performance];
                const maxValue = Math.max(...agents.map(a => a.performance[metric as keyof typeof a.performance]));
                const percentage = (Number(value) / maxValue) * 100;
                
                return (
                  <div key={agent.agentId} className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                        {agent.agentName}
                      </span>
                      <span className="text-sm text-gray-600 dark:text-gray-400">
                        {typeof value === 'number' 
                          ? metric.includes('Rate') 
                            ? `${value.toFixed(1)}%`
                            : metric.includes('Time')
                              ? `${value.toFixed(0)}ms`
                              : value.toLocaleString()
                          : value
                        }
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                      <motion.div
                        className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full"
                        initial={{ width: 0 }}
                        animate={{ width: `${percentage}%` }}
                        transition={{ duration: 1, delay: agentIndex * 0.1 }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </motion.div>
        ))}
      </div>
    );
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header Controls */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            Agent Performance
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            Real-time metrics and performance monitoring
          </p>
        </div>

        <div className="flex items-center gap-2">
          {/* Sort Controls */}
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as any)}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
          >
            <option value="name">Sort by Name</option>
            <option value="performance">Sort by Performance</option>
            <option value="activity">Sort by Activity</option>
          </select>

          {/* View Mode Toggles */}
          <div className="flex border border-gray-300 dark:border-gray-600 rounded-lg overflow-hidden">
            {(['grid', 'list', 'comparison'] as const).map((mode) => (
              <button
                key={mode}
                onClick={() => setViewMode(mode)}
                className={`px-3 py-2 text-sm font-medium transition-colors ${
                  viewMode === mode
                    ? 'bg-blue-500 text-white'
                    : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
                }`}
              >
                {mode === 'grid' && <BarChart3 className="w-4 h-4" />}
                {mode === 'list' && <Activity className="w-4 h-4" />}
                {mode === 'comparison' && <PieChart className="w-4 h-4" />}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Overall Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          {
            label: 'Total Agents',
            value: agents.length,
            icon: Activity,
            color: 'text-blue-500'
          },
          {
            label: 'Active Agents',
            value: agents.filter(a => a.status === 'active').length,
            icon: CheckCircle,
            color: 'text-green-500'
          },
          {
            label: 'Avg Success Rate',
            value: `${(agents.reduce((sum, a) => sum + a.performance.successRate, 0) / agents.length).toFixed(1)}%`,
            icon: Target,
            color: 'text-purple-500'
          },
          {
            label: 'Total Tasks',
            value: agents.reduce((sum, a) => sum + a.performance.tasksCompleted, 0),
            icon: TrendingUp,
            color: 'text-orange-500'
          }
        ].map((stat, index) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
            className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700"
          >
            <div className="flex items-center gap-3">
              <div className={`p-2 rounded-lg bg-gray-100 dark:bg-gray-700 ${stat.color}`}>
                <stat.icon className="w-5 h-5" />
              </div>
              <div>
                <div className="text-sm text-gray-600 dark:text-gray-400">{stat.label}</div>
                <div className="text-xl font-bold text-gray-900 dark:text-gray-100">{stat.value}</div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Content */}
      <AnimatePresence mode="wait">
        {viewMode === 'comparison' ? (
          <motion.div
            key="comparison"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            {renderComparisonView()}
          </motion.div>
        ) : (
          <motion.div
            key="grid-list"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className={viewMode === 'grid' ? 'grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6' : 'space-y-4'}
          >
            {sortedAgents.map((agent, index) => renderMetricCard(agent, index))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
