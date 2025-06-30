'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Activity,
  AlertTriangle,
  Clock,
  Heart,
  Cpu,
  HardDrive,
  Wifi,
  ThermometerSun,
  RefreshCw,
  Settings,
  TrendingUp,
  Minus
} from 'lucide-react';

interface HealthMetric {
  name: string;
  value: number;
  unit: string;
  status: 'healthy' | 'warning' | 'critical';
  threshold: {
    warning: number;
    critical: number;
  };
  trend?: 'up' | 'down' | 'stable';
}

interface AgentHealth {
  agentId: string;
  agentName: string;
  status: 'online' | 'offline' | 'degraded' | 'maintenance';
  lastHeartbeat: Date;
  uptime: number;
  version: string;
  environment: string;
  metrics: {
    cpu: HealthMetric;
    memory: HealthMetric;
    disk: HealthMetric;
    network: HealthMetric;
    temperature?: HealthMetric;
    responseTime: HealthMetric;
    errorRate: HealthMetric;
    throughput: HealthMetric;
  };
  alerts: Array<{
    id: string;
    severity: 'info' | 'warning' | 'error' | 'critical';
    message: string;
    timestamp: Date;
    acknowledged: boolean;
  }>;
  endpoints: Array<{
    name: string;
    url: string;
    status: 'healthy' | 'unhealthy' | 'unknown';
    lastCheck: Date;
    responseTime: number;
  }>;
}

interface AgentHealthMonitorProps {
  agents: AgentHealth[];
  refreshInterval?: number;
  onAgentSelect?: (agentId: string) => void;
  onAlertAcknowledge?: (agentId: string, alertId: string) => void;
  onAgentRestart?: (agentId: string) => void;
  onRefreshHealth?: (agentId: string) => void;
  className?: string;
  compactMode?: boolean;
}

export function AgentHealthMonitor({
  agents,
  refreshInterval = 30000,
  onAgentSelect,
  onAlertAcknowledge,
  onAgentRestart,
  onRefreshHealth,
  className = '',
  compactMode = false
}: Readonly<AgentHealthMonitorProps>) {
  const [lastRefresh, setLastRefresh] = useState(new Date());

  // Auto-refresh
  useEffect(() => {
    if (refreshInterval > 0) {
      const interval = setInterval(() => {
        setLastRefresh(new Date());
      }, refreshInterval);
      
      return () => clearInterval(interval);
    }
  }, [refreshInterval]);

  const getStatusColor = (status: AgentHealth['status']) => {
    switch (status) {
      case 'online':
        return {
          bg: 'bg-green-100 dark:bg-green-900/20',
          text: 'text-green-800 dark:text-green-300',
          dot: 'bg-green-500',
          pulse: 'animate-pulse'
        };
      case 'degraded':
        return {
          bg: 'bg-yellow-100 dark:bg-yellow-900/20',
          text: 'text-yellow-800 dark:text-yellow-300',
          dot: 'bg-yellow-500',
          pulse: 'animate-pulse'
        };
      case 'offline':
        return {
          bg: 'bg-red-100 dark:bg-red-900/20',
          text: 'text-red-800 dark:text-red-300',
          dot: 'bg-red-500',
          pulse: ''
        };
      case 'maintenance':
        return {
          bg: 'bg-blue-100 dark:bg-blue-900/20',
          text: 'text-blue-800 dark:text-blue-300',
          dot: 'bg-blue-500',
          pulse: 'animate-pulse'
        };
    }
  };

  const getMetricColor = (status: HealthMetric['status']) => {
    switch (status) {
      case 'healthy':
        return 'text-green-600 dark:text-green-400';
      case 'warning':
        return 'text-yellow-600 dark:text-yellow-400';
      case 'critical':
        return 'text-red-600 dark:text-red-400';
    }
  };

  const getMetricBarColor = (status: HealthMetric['status']) => {
    switch (status) {
      case 'critical':
        return 'bg-red-500';
      case 'warning':
        return 'bg-yellow-500';
      case 'healthy':
      default:
        return 'bg-green-500';
    }
  };

  const getMetricIcon = (metricName: string) => {
    switch (metricName.toLowerCase()) {
      case 'cpu':
        return <Cpu className="w-4 h-4" />;
      case 'memory':
        return <HardDrive className="w-4 h-4" />;
      case 'disk':
        return <HardDrive className="w-4 h-4" />;
      case 'network':
        return <Wifi className="w-4 h-4" />;
      case 'temperature':
        return <ThermometerSun className="w-4 h-4" />;
      case 'responsetime':
        return <Clock className="w-4 h-4" />;
      case 'errorrate':
        return <AlertTriangle className="w-4 h-4" />;
      case 'throughput':
        return <Activity className="w-4 h-4" />;
      default:
        return <Activity className="w-4 h-4" />;
    }
  };

  const getTrendIcon = (trend?: HealthMetric['trend']) => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="w-3 h-3 text-red-500" />;
      case 'down':
        return <TrendingUp className="w-3 h-3 text-green-500" />;
      case 'stable':
        return <Minus className="w-3 h-3 text-gray-400" />;
      default:
        return null;
    }
  };

  const formatUptime = (uptime: number) => {
    const days = Math.floor(uptime / (24 * 60 * 60 * 1000));
    const hours = Math.floor((uptime % (24 * 60 * 60 * 1000)) / (60 * 60 * 1000));
    const minutes = Math.floor((uptime % (60 * 60 * 1000)) / (60 * 1000));
    
    if (days > 0) return `${days}d ${hours}h`;
    if (hours > 0) return `${hours}h ${minutes}m`;
    return `${minutes}m`;
  };

  const getOverallHealth = (agent: AgentHealth): 'healthy' | 'warning' | 'critical' => {
    if (agent.status === 'offline') return 'critical';
    if (agent.status === 'degraded') return 'warning';
    
    const metrics = Object.values(agent.metrics);
    const criticalMetrics = metrics.filter(m => m.status === 'critical');
    const warningMetrics = metrics.filter(m => m.status === 'warning');
    
    if (criticalMetrics.length > 0) return 'critical';
    if (warningMetrics.length > 0) return 'warning';
    return 'healthy';
  };

  const renderStatusLight = (agent: AgentHealth) => {
    const statusColors = getStatusColor(agent.status);
    const overallHealth = getOverallHealth(agent);
    
    return (
      <div className="relative">
        <div className={`w-3 h-3 rounded-full ${statusColors.dot} ${statusColors.pulse}`} />
        {overallHealth !== 'healthy' && (
          <div className="absolute -top-1 -right-1 w-2 h-2 bg-red-500 rounded-full animate-pulse" />
        )}
      </div>
    );
  };

  const renderMetricCard = (metric: HealthMetric, name: string) => {
    return (
      <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <div className={getMetricColor(metric.status)}>
              {getMetricIcon(name)}
            </div>
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
              {metric.name}
            </span>
          </div>
          {getTrendIcon(metric.trend)}
        </div>
        
        <div className="flex items-center justify-between">
          <span className={`text-lg font-bold ${getMetricColor(metric.status)}`}>
            {metric.value.toFixed(1)}{metric.unit}
          </span>
          
          <div className="text-xs text-gray-500 dark:text-gray-400">
            W: {metric.threshold.warning}{metric.unit} | 
            C: {metric.threshold.critical}{metric.unit}
          </div>
        </div>
        
        {/* Progress Bar */}
        <div className="mt-2 w-full bg-gray-200 dark:bg-gray-600 rounded-full h-1.5">
          <div
            className={`h-1.5 rounded-full transition-all duration-500 ${getMetricBarColor(metric.status)}`}
            style={{
              width: `${Math.min((metric.value / metric.threshold.critical) * 100, 100)}%`
            }}
          />
        </div>
      </div>
    );
  };

  const renderCompactAgent = (agent: AgentHealth, index: number) => {
    const unacknowledgedAlerts = agent.alerts.filter(a => !a.acknowledged);
    
    return (
      <motion.div
        key={agent.agentId}
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.2, delay: index * 0.05 }}
        className={`
          bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700
          hover:border-blue-300 dark:hover:border-blue-600 transition-all duration-200
          cursor-pointer p-3
        `}
        onClick={() => onAgentSelect?.(agent.agentId)}
      >
        <div className="flex items-center gap-3">
          {renderStatusLight(agent)}
          
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between">
              <h3 className="font-medium text-gray-900 dark:text-gray-100 truncate">
                {agent.agentName}
              </h3>
              
              {unacknowledgedAlerts.length > 0 && (
                <div className="bg-red-100 dark:bg-red-900/20 text-red-800 dark:text-red-300 px-2 py-1 rounded-full text-xs font-medium">
                  {unacknowledgedAlerts.length}
                </div>
              )}
            </div>
            
            <div className="text-sm text-gray-600 dark:text-gray-400">
              {agent.status} • {formatUptime(agent.uptime)} uptime
            </div>
          </div>
          
          <div className="flex items-center gap-1">
            {Object.entries(agent.metrics).slice(0, 4).map(([name, metric]) => (
              <div
                key={name}
                className={`w-2 h-6 rounded-full ${
                  metric.status === 'critical' ? 'bg-red-500' :
                  metric.status === 'warning' ? 'bg-yellow-500' : 'bg-green-500'
                }`}
                title={`${metric.name}: ${metric.value}${metric.unit}`}
              />
            ))}
          </div>
        </div>
      </motion.div>
    );
  };

  const renderDetailedAgent = (agent: AgentHealth, index: number) => {
    const statusColors = getStatusColor(agent.status);
    const unacknowledgedAlerts = agent.alerts.filter(a => !a.acknowledged);
    
    return (
      <motion.div
        key={agent.agentId}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: index * 0.1 }}
        className={`
          bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700
          hover:border-blue-300 dark:hover:border-blue-600 transition-all duration-200
        `}
      >
        {/* Header */}
        <div className="p-4 border-b border-gray-100 dark:border-gray-700">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-3">
              {renderStatusLight(agent)}
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-gray-100">
                  {agent.agentName}
                </h3>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  {agent.agentId} • v{agent.version}
                </div>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <button
                onClick={() => onRefreshHealth?.(agent.agentId)}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                title="Refresh health"
              >
                <RefreshCw className="w-4 h-4" />
              </button>
              <button
                onClick={() => onAgentRestart?.(agent.agentId)}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                title="Restart agent"
              >
                <Settings className="w-4 h-4" />
              </button>
            </div>
          </div>
          
          <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium ${statusColors.bg} ${statusColors.text}`}>
            <Heart className="w-4 h-4" />
            {agent.status} • {formatUptime(agent.uptime)} uptime
          </div>
        </div>

        {/* Metrics Grid */}
        <div className="p-4">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-4">
            {Object.entries(agent.metrics).map(([name, metric]) => 
              renderMetricCard(metric, name)
            )}
          </div>

          {/* Endpoints */}
          {agent.endpoints.length > 0 && (
            <div className="mb-4">
              <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Endpoints
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {agent.endpoints.map((endpoint, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-700 rounded"
                  >
                    <div className="flex items-center gap-2">
                      <div className={`w-2 h-2 rounded-full ${
                        endpoint.status === 'healthy' ? 'bg-green-500' :
                        endpoint.status === 'unhealthy' ? 'bg-red-500' : 'bg-gray-400'
                      }`} />
                      <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                        {endpoint.name}
                      </span>
                    </div>
                    <span className="text-xs text-gray-500 dark:text-gray-400">
                      {endpoint.responseTime}ms
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Alerts */}
          {unacknowledgedAlerts.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Active Alerts ({unacknowledgedAlerts.length})
              </h4>
              <div className="space-y-2">
                {unacknowledgedAlerts.slice(0, 3).map((alert) => (
                  <div
                    key={alert.id}
                    className={`p-3 rounded-lg border-l-4 ${
                      alert.severity === 'critical' ? 'bg-red-50 dark:bg-red-900/20 border-red-500' :
                      alert.severity === 'error' ? 'bg-red-50 dark:bg-red-900/20 border-red-400' :
                      alert.severity === 'warning' ? 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-500' :
                      'bg-blue-50 dark:bg-blue-900/20 border-blue-500'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="text-sm font-medium text-gray-900 dark:text-gray-100">
                          {alert.message}
                        </div>
                        <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                          {alert.timestamp.toLocaleString()}
                        </div>
                      </div>
                      
                      <button
                        onClick={() => onAlertAcknowledge?.(agent.agentId, alert.id)}
                        className="text-xs px-2 py-1 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors"
                      >
                        Acknowledge
                      </button>
                    </div>
                  </div>
                ))}
                
                {unacknowledgedAlerts.length > 3 && (
                  <div className="text-sm text-gray-600 dark:text-gray-400 text-center py-2">
                    +{unacknowledgedAlerts.length - 3} more alerts
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </motion.div>
    );
  };

  // Overall system health
  const overallHealth = agents.reduce((acc, agent) => {
    const health = getOverallHealth(agent);
    if (health === 'critical') acc.critical++;
    else if (health === 'warning') acc.warning++;
    else acc.healthy++;
    return acc;
  }, { healthy: 0, warning: 0, critical: 0 });

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            Agent Health Monitor
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            Last updated: {lastRefresh.toLocaleTimeString()}
          </p>
        </div>

        {/* System Health Overview */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-green-500 rounded-full" />
            <span className="text-sm text-gray-600 dark:text-gray-400">
              Healthy: {overallHealth.healthy}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-yellow-500 rounded-full" />
            <span className="text-sm text-gray-600 dark:text-gray-400">
              Warning: {overallHealth.warning}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-red-500 rounded-full" />
            <span className="text-sm text-gray-600 dark:text-gray-400">
              Critical: {overallHealth.critical}
            </span>
          </div>
        </div>
      </div>

      {/* Agents */}
      <div className={compactMode ? 'space-y-3' : 'grid grid-cols-1 lg:grid-cols-2 gap-6'}>
        <AnimatePresence>
          {agents.map((agent, index) => 
            compactMode 
              ? renderCompactAgent(agent, index)
              : renderDetailedAgent(agent, index)
          )}
        </AnimatePresence>
      </div>

      {/* Empty State */}
      {agents.length === 0 && (
        <div className="text-center py-12">
          <div className="text-gray-400 dark:text-gray-600 mb-4">
            <Heart className="w-12 h-12 mx-auto" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
            No agents found
          </h3>
          <p className="text-gray-600 dark:text-gray-400">
            No agents are currently registered for health monitoring.
          </p>
        </div>
      )}
    </div>
  );
}
