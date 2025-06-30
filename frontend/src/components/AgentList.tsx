'use client';

import { useState } from 'react';
import {
  MessageCircle, BarChart, Lightbulb, ChevronDown, Target, 
  AlertCircle, CheckCircle2, Clock, Database, TrendingUp, Brain, Network, Settings
} from "lucide-react";
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNotifications } from '@/components/ui/notification';

interface AgentMetrics {
  executionTime?: number;
  dataProcessed?: number;
  accuracy?: number;
  memoryUsage?: number;
  tokensUsed?: number;
}

interface AgentCapabilities {
  planning: boolean;
  dataAnalysis: boolean;
  nlpProcessing: boolean;
  insightGeneration: boolean;
  memoryAccess: boolean;
  toolUsage: boolean;
}

interface Agent {
  id: string;
  icon: React.ReactNode;
  name: string;
  status: 'idle' | 'processing' | 'complete' | 'error' | 'queued' | 'paused' | 'waiting';
  description: string;
  progress?: number;
  lastUpdate?: string;
  error?: string;
  metrics?: AgentMetrics;
  capabilities?: AgentCapabilities;
  dependencies?: string[];
  priority?: number;
  workflowPosition?: number;
}

interface WorkflowExecution {
  sessionId: string;
  isRunning: boolean;
  isPaused: boolean;
  currentAgent?: string;
  currentStep?: string;
  progress: Record<string, number>;
  statuses: Record<string, Agent['status']>;
  results: Record<string, any>;
  errors: Record<string, string>;
  startTime?: number;
  estimatedCompletion?: number;
  totalSteps?: number;
  completedSteps?: number;
}

interface SystemMetrics {
  activeAgents: number;
  completedTasks: number;
  errorRate: number;
  avgExecutionTime: number;
  memoryUsage: number;
  cpuUsage: number;
}

const initialAgents: Agent[] = [
  { 
    id: 'planning',
    icon: <Target size={20} />, 
    name: "Planning Agent",
    status: 'idle',
    description: "Orchestrates workflow and creates strategic analysis plans",
    capabilities: {
      planning: true,
      dataAnalysis: false,
      nlpProcessing: true,
      insightGeneration: false,
      memoryAccess: true,
      toolUsage: true
    },
    dependencies: [],
    priority: 1,
    workflowPosition: 1
  },
  { 
    id: 'data_analysis',
    icon: <BarChart size={20} />, 
    name: "Data Analysis Agent",
    status: 'idle',
    description: "Processes and analyzes data with advanced ML algorithms",
    capabilities: {
      planning: false,
      dataAnalysis: true,
      nlpProcessing: false,
      insightGeneration: false,
      memoryAccess: true,
      toolUsage: true
    },
    dependencies: ['planning'],
    priority: 2,
    workflowPosition: 2
  },
  { 
    id: 'query',
    icon: <MessageCircle size={20} />, 
    name: "Query Agent",
    status: 'idle',
    description: "Handles natural language queries and intelligent data retrieval",
    capabilities: {
      planning: false,
      dataAnalysis: false,
      nlpProcessing: true,
      insightGeneration: false,
      memoryAccess: true,
      toolUsage: true
    },
    dependencies: ['data_analysis'],
    priority: 3,
    workflowPosition: 3
  },
  { 
    id: 'insight',
    icon: <Lightbulb size={20} />, 
    name: "Insight Agent",
    status: 'idle',
    description: "Generates actionable insights and strategic recommendations",
    capabilities: {
      planning: false,
      dataAnalysis: false,
      nlpProcessing: true,
      insightGeneration: true,
      memoryAccess: true,
      toolUsage: false
    },
    dependencies: ['query'],
    priority: 4,
    workflowPosition: 4
  }
];

const getStatusColor = (status: Agent['status']) => {
  switch (status) {
    case 'processing':
      return 'text-cyan-400 border-cyan-400/30 bg-cyan-400/10 shadow-cyan-400/20';
    case 'complete':
      return 'text-green-400 border-green-400/30 bg-green-400/10 shadow-green-400/20';
    case 'error':
      return 'text-red-400 border-red-400/30 bg-red-400/10 shadow-red-400/20';
    case 'queued':
      return 'text-amber-400 border-amber-400/30 bg-amber-400/10 shadow-amber-400/20';
    case 'paused':
      return 'text-purple-400 border-purple-400/30 bg-purple-400/10 shadow-purple-400/20';
    case 'waiting':
      return 'text-blue-400 border-blue-400/30 bg-blue-400/10 shadow-blue-400/20';
    default:
      return 'text-gray-300 border-white/10 bg-white/5 shadow-black/20';
  }
};

const getStatusDot = (status: Agent['status']) => {
  switch (status) {
    case 'processing':
      return 'bg-cyan-400 animate-pulse shadow-lg shadow-cyan-400/50';
    case 'complete':
      return 'bg-green-400 shadow-lg shadow-green-400/50';
    case 'error':
      return 'bg-red-400 animate-bounce shadow-lg shadow-red-400/50';
    case 'queued':
      return 'bg-amber-400 animate-ping shadow-lg shadow-amber-400/50';
    case 'paused':
      return 'bg-purple-400 shadow-lg shadow-purple-400/50';
    case 'waiting':
      return 'bg-blue-400 animate-pulse shadow-lg shadow-blue-400/50';
    default:
      return 'bg-gray-500';
  }
};

const getProgressBarColor = (status: Agent['status']) => {
  switch (status) {
    case 'processing':
      return 'bg-gradient-to-r from-cyan-400 to-blue-500';
    case 'queued':
      return 'bg-gradient-to-r from-amber-400 to-orange-500';
    default:
      return 'bg-gradient-to-r from-blue-400 to-purple-500';
  }
};

const getWorkflowStepStyle = (status: Agent['status']) => {
  switch (status) {
    case 'complete':
      return 'border-green-400 bg-green-400/20 text-green-400';
    case 'processing':
      return 'border-cyan-400 bg-cyan-400/20 text-cyan-400 animate-pulse';
    case 'error':
      return 'border-red-400 bg-red-400/20 text-red-400';
    case 'queued':
      return 'border-amber-400 bg-amber-400/20 text-amber-400';
    case 'waiting':
      return 'border-blue-400 bg-blue-400/20 text-blue-400';
    default:
      return 'border-gray-500 bg-gray-500/20 text-gray-500';
  }
};

const getStatusText = (status: Agent['status'], progress?: number) => {
  switch (status) {
    case 'processing':
      return progress ? `Processing... ${Math.round(progress)}%` : 'Processing...';
    case 'complete':
      return 'Completed Successfully';
    case 'error':
      return 'Error Occurred';
    case 'queued':
      return 'Queued for Execution';
    case 'paused':
      return 'Paused';
    case 'waiting':
      return 'Waiting for Dependencies';
    default:
      return 'Ready to Execute';
  }
};

export default function AgentList() {
  const [expandedAgent, setExpandedAgent] = useState<string | null>(null);
  const { addNotification } = useNotifications();
  const queryClient = useQueryClient();

  // Agent workflow execution mutation
  const executeWorkflow = useMutation({
    mutationFn: async (query: string) => {
      const response = await fetch('http://localhost:8000/api/v1/agents/workflow/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      });
      if (!response.ok) throw new Error('Failed to start workflow');
      return response.json();
    },
    onSuccess: (data) => {
      addNotification({ type: 'success', title: 'Workflow started', message: `Session: ${data.session_id}` });
      queryClient.invalidateQueries({ queryKey: ['agent-status', data.session_id] });
    },
    onError: (error: any) => {
      addNotification({ type: 'error', title: 'Workflow error', message: error.message });
    },
  });

  // Agent status polling
  const { data: agentStatus, isLoading, isError, refetch } = useQuery({
    queryKey: ['agent-status'],
    queryFn: async () => {
      const response = await fetch('http://localhost:8000/api/v1/agents/workflow/status/current');
      if (!response.ok) throw new Error('Failed to fetch agent status');
      return response.json();
    },
    refetchInterval: 2000,
  });

  // Accessibility: keyboard navigation for agent cards
  const handleAgentCardKeyDown = (event: React.KeyboardEvent, agentId: string) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      setExpandedAgent(expandedAgent === agentId ? null : agentId);
    }
  };

  if (isLoading) {
    return <output className="p-6 text-center text-gray-400" aria-live="polite">Loading agent workflow...</output>;
  }
  if (isError) {
    return <div className="p-6 text-center text-red-500" role="alert">Failed to load agent workflow. <button onClick={() => refetch()} className="underline">Retry</button></div>;
  }

  // Render agent list from agentStatus
  const agents = agentStatus?.agents ?? [];
  const workflowRunning = agentStatus?.isRunning;
  const sessionId = agentStatus?.session_id;
  const systemMetrics = agentStatus?.systemMetrics ?? {};

  return (
    <div className="flex flex-col gap-4" aria-label="Agent Workflow List">
      {/* Control Panel */}
      <div className="backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl p-4 shadow-2xl shadow-black/25">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-3">
            <div className={`w-3 h-3 rounded-full ${agentStatus?.connected ? 'bg-green-400 animate-pulse' : 'bg-red-400'}`} />
            <span className="text-sm font-medium text-gray-300">
              Agent System {agentStatus?.connected ? 'Connected' : 'Disconnected'}
            </span>
            <div className="flex items-center gap-2 text-xs text-gray-400">
              <span>{systemMetrics.activeAgents ?? 0} active</span>
            </div>
          </div>
          <div className="text-xs text-gray-400">
            Session: {sessionId ? String(sessionId).slice(-8) : 'N/A'}
          </div>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => executeWorkflow.mutate('Analyze uploaded data')}
            disabled={(workflowRunning ?? false) || !(agentStatus?.connected ?? false)}
            className="flex items-center gap-2 px-4 py-2 bg-cyan-500/20 border border-cyan-500/30 rounded-lg text-cyan-400 text-sm font-medium hover:bg-cyan-500/30 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300"
          >
            Start Analysis
          </button>
          <button
            onClick={() => addNotification({ type: 'info', title: 'Stop not implemented' })}
            disabled={!workflowRunning}
            className="flex items-center gap-2 px-4 py-2 bg-red-500/20 border border-red-500/30 rounded-lg text-red-400 text-sm font-medium hover:bg-red-500/30 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300"
          >
            Stop
          </button>
          <button
            onClick={() => addNotification({ type: 'info', title: 'Reset not implemented' })}
            disabled={workflowRunning}
            className="flex items-center gap-2 px-4 py-2 bg-gray-500/20 border border-gray-500/30 rounded-lg text-gray-400 text-sm font-medium hover:bg-gray-500/30 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300"
          >
            Reset
          </button>
        </div>
      </div>
      {/* Agent List */}
      <div className="flex flex-col gap-3">
        {agents.map((agent: any, index: number) => (
          <div key={agent.id} className="relative">
            <button
              type="button"
              aria-expanded={expandedAgent === agent.id}
              aria-label={`${agent.name} - ${agent.status}`}
              className={`backdrop-blur-md border rounded-2xl p-4 transition-all duration-300 cursor-pointer group relative overflow-hidden focus:outline-none focus:ring-2 focus:ring-cyan-400/50 ${getStatusColor(agent.status)}`}
              onClick={() => setExpandedAgent(expandedAgent === agent.id ? null : agent.id)}
              onKeyDown={(e) => handleAgentCardKeyDown(e, agent.id)}
            >
              {/* Background Glow Effect */}
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
              
              <div className="flex items-center justify-between relative z-10">
                <div className="flex items-center gap-4">
                  {/* Enhanced Agent Icon */}
                  <div className="flex items-center justify-center w-12 h-12 rounded-xl backdrop-blur-sm bg-white/10 border border-white/20 shadow-lg relative">
                    {agent.icon}
                    {/* Workflow Position Indicator */}
                    <div className="absolute -top-1 -right-1 w-5 h-5 bg-gradient-to-br from-cyan-400 to-blue-500 rounded-full flex items-center justify-center text-xs font-bold text-white">
                      {agent.workflowPosition}
                    </div>
                  </div>
                  
                  {/* Agent Info */}
                  <div className="flex flex-col">
                    <div className="flex items-center gap-3">
                      <span className="font-semibold text-base">{agent.name}</span>
                      <div className={`w-3 h-3 rounded-full ${getStatusDot(agent.status)}`} />
                      <span className="text-xs font-medium">
                        {getStatusText(agent.status, agent.progress)}
                      </span>
                    </div>
                    <span className="text-sm text-gray-400 group-hover:text-gray-300 transition-colors">
                      {agent.description}
                    </span>
                    
                    {/* Enhanced Progress Bar */}
                    {['processing', 'queued', 'waiting'].includes(agent.status) && agent.progress !== undefined && (
                      <div className="mt-2 w-48 h-2 bg-white/10 rounded-full overflow-hidden">
                        <div 
                          className={`h-full transition-all duration-500 ease-out ${getProgressBarColor(agent.status)}`}
                          style={{ width: `${agent.progress}%` }}
                        />
                      </div>
                    )}

                    {/* Agent Capabilities Indicators */}
                    {agent.capabilities && (
                      <div className="flex gap-1 mt-1">
                        {agent.capabilities.planning && <Brain size={10} className="text-purple-400" />}
                        {agent.capabilities.dataAnalysis && <Database size={10} className="text-green-400" />}
                        {agent.capabilities.nlpProcessing && <MessageCircle size={10} className="text-blue-400" />}
                        {agent.capabilities.insightGeneration && <Lightbulb size={10} className="text-yellow-400" />}
                        {agent.capabilities.memoryAccess && <Network size={10} className="text-cyan-400" />}
                        {agent.capabilities.toolUsage && <Settings size={10} className="text-gray-400" />}
                      </div>
                    )}
                  </div>
                </div>
                
                {/* Status and Expand Button */}
                <div className="flex items-center gap-3">
                  {/* Current Step Indicator */}
                  {agentStatus.currentAgent === agent.id && agentStatus.currentStep && (
                    <div className="text-xs text-cyan-400 bg-cyan-400/10 px-2 py-1 rounded">
                      {agentStatus.currentStep}
                    </div>
                  )}
                  
                  <ChevronDown 
                    className={`w-5 h-5 text-gray-400 group-hover:text-gray-300 transition-all duration-300 ${
                      expandedAgent === agent.id ? 'rotate-180' : ''
                    }`} 
                  />
                </div>
              </div>                {/* Enhanced Metrics Display */}
                {agent.metrics && (agentStatus.isRunning || agentStatus.isPaused || agent.status === 'complete') && (
                  <div className="mt-3 grid grid-cols-3 gap-2 text-xs">
                    {agent.metrics.executionTime && agent.metrics.executionTime > 0 && (
                      <div className="flex items-center gap-1 text-gray-400">
                        <Clock size={10} />
                        <span>{agent.metrics.executionTime}ms</span>
                      </div>
                    )}
                    {agent.metrics.dataProcessed && agent.metrics.dataProcessed > 0 && (
                      <div className="flex items-center gap-1 text-gray-400">
                        <Database size={10} />
                        <span>{agent.metrics.dataProcessed} records</span>
                      </div>
                    )}
                    {agent.metrics.accuracy && agent.metrics.accuracy > 0 && (
                      <div className="flex items-center gap-1 text-gray-400">
                        <TrendingUp size={10} />
                        <span>{agent.metrics.accuracy.toFixed(1)}%</span>
                      </div>
                    )}
                  </div>
                )}

              {/* Error Display */}
              {agent.error && (
                <div className="mt-2 flex items-start gap-2 text-xs text-red-400 bg-red-400/10 border border-red-400/20 rounded-lg p-2">
                  <AlertCircle size={12} className="flex-shrink-0 mt-0.5" />
                  <span>{agent.error}</span>
                </div>
              )}
            </button>
            {/* Expanded Details */}
            {expandedAgent === agent.id && (
              <div className="mt-2 backdrop-blur-md bg-white/5 border border-white/10 rounded-xl p-4 shadow-lg">
                <div className="grid grid-cols-2 gap-4 text-sm mb-4">
                  <div>
                    <span className="text-gray-400">Status:</span>
                    <span className="ml-2 font-medium capitalize">{agent.status}</span>
                  </div>
                  <div>
                    <span className="text-gray-400">Progress:</span>
                    <span className="ml-2 font-medium">{agent.progress ?? 0}%</span>
                  </div>
                  <div>
                    <span className="text-gray-400">Last Update:</span>
                    <span className="ml-2 font-medium">
                      {agent.lastUpdate ? new Date(agent.lastUpdate).toLocaleTimeString() : 'Never'}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-400">Priority:</span>
                    <span className="ml-2 font-medium">{agent.priority}</span>
                  </div>
                </div>

                {/* Agent Dependencies */}
                {agent.dependencies && agent.dependencies.length > 0 && (
                  <div className="mb-4">
                    <div className="text-sm font-medium text-gray-300 mb-2">Dependencies:</div>
                    <div className="flex flex-wrap gap-1">
                      {agent.dependencies.map((dep: string) => (
                        <span key={dep} className="text-xs bg-blue-500/20 text-blue-400 px-2 py-1 rounded">
                          {dep}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Enhanced Capabilities */}
                {agent.capabilities && (
                  <div className="mb-4">
                    <div className="text-sm font-medium text-gray-300 mb-2">Capabilities:</div>
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      {Object.entries(agent.capabilities).map(([key, enabled]) => (
                        <div key={key} className={`flex items-center gap-2 ${enabled ? 'text-green-400' : 'text-gray-500'}`}>
                          {enabled ? <CheckCircle2 size={12} /> : <AlertCircle size={12} />}
                          <span className="capitalize">{key.replace(/([A-Z])/g, ' $1').trim()}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Enhanced Metrics */}
                {agent.metrics && (
                  <div className="mb-4">
                    <div className="text-sm font-medium text-gray-300 mb-2">Performance Metrics:</div>
                    <div className="grid grid-cols-2 gap-3">
                      {agent.metrics.executionTime && agent.metrics.executionTime > 0 && (
                        <div className="bg-white/5 rounded-lg p-2">
                          <div className="text-xs text-gray-400">Execution Time</div>
                          <div className="text-cyan-400 font-semibold">{agent.metrics.executionTime}ms</div>
                        </div>
                      )}
                      {agent.metrics.dataProcessed && agent.metrics.dataProcessed > 0 && (
                        <div className="bg-white/5 rounded-lg p-2">
                          <div className="text-xs text-gray-400">Data Processed</div>
                          <div className="text-green-400 font-semibold">{agent.metrics.dataProcessed}</div>
                        </div>
                      )}
                      {agent.metrics.accuracy && agent.metrics.accuracy > 0 && (
                        <div className="bg-white/5 rounded-lg p-2">
                          <div className="text-xs text-gray-400">Accuracy</div>
                          <div className="text-purple-400 font-semibold">{agent.metrics.accuracy.toFixed(1)}%</div>
                        </div>
                      )}
                      {agent.metrics.memoryUsage && agent.metrics.memoryUsage > 0 && (
                        <div className="bg-white/5 rounded-lg p-2">
                          <div className="text-xs text-gray-400">Memory Usage</div>
                          <div className="text-amber-400 font-semibold">{agent.metrics.memoryUsage.toFixed(1)}MB</div>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Agent Results */}
                {agentStatus.results[agent.id] && (
                  <div className="mb-3">
                    <div className="text-sm font-medium text-gray-300 mb-2">Execution Results:</div>
                    <div className="bg-white/5 rounded-lg p-3 max-h-40 overflow-y-auto">
                      <pre className="text-xs text-gray-400 whitespace-pre-wrap">
                        {JSON.stringify(agentStatus.results[agent.id], null, 2)}
                      </pre>
                    </div>
                  </div>
                )}

                {/* Agent ID */}
                <div className="text-xs text-gray-500">
                  <span>Agent ID: </span>
                  <span className="font-mono">{agent.id}</span>
                </div>
              </div>
            )}

            {/* Enhanced Workflow Connection Lines */}
            {index < agents.length - 1 && (
              <div className="flex justify-center my-2">
                <div className="w-0.5 h-4 bg-gradient-to-b from-white/30 via-cyan-400/50 to-white/30 relative">
                  <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-2 h-2 bg-cyan-400 rounded-full animate-pulse" />
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
      {/* Workflow Execution Info */}
      {workflowRunning && (
        <div className="backdrop-blur-md bg-white/5 border border-white/10 rounded-xl p-4 shadow-lg">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-300">
              Workflow Executing: {agentStatus?.currentAgent ?? 'Initializing...'}
            </span>
            <div className="flex items-center gap-2 text-xs text-gray-400">
              <div className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse" />
              Running for {agentStatus?.startTime ? Math.round((Date.now() - agentStatus.startTime) / 1000) : 0}s
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
