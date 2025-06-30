'use client';

import { useState, useEffect, useCallback } from 'react';
import {
  MessageCircle, BarChart, Lightbulb, ChevronDown, Target, 
  Play, Square, RotateCcw, Activity, AlertCircle, CheckCircle2,
  Clock, Database, TrendingUp, Brain, Network, Settings
} from "lucide-react";

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
  const [agents, setAgents] = useState<Agent[]>(initialAgents);
  const [execution, setExecution] = useState<WorkflowExecution>({
    sessionId: '',
    isRunning: false,
    isPaused: false,
    progress: {},
    statuses: {},
    results: {},
    errors: {},
    totalSteps: initialAgents.length,
    completedSteps: 0
  });
  const [isConnected, setIsConnected] = useState(false);
  const [expandedAgent, setExpandedAgent] = useState<string | null>(null);
  const [systemMetrics, setSystemMetrics] = useState<SystemMetrics>({
    activeAgents: 0,
    completedTasks: 0,
    errorRate: 0,
    avgExecutionTime: 0,
    memoryUsage: 0,
    cpuUsage: 0
  });

  // Check backend connection and system health
  const checkConnection = useCallback(async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/health');
      if (response.ok) {
        const healthData = await response.json();
        setIsConnected(true);
        
        // Update system metrics if available
        if (healthData.metrics) {
          setSystemMetrics(prev => ({
            ...prev,
            ...healthData.metrics
          }));
        }
      } else {
        setIsConnected(false);
        console.warn('Backend health check failed:', response.status);
      }
    } catch (error) {
      console.error('Backend connection failed:', error);
      setIsConnected(false);
    }
  }, []);

  // Fetch comprehensive agent execution status and workflow state
  const fetchAgentStatus = useCallback(async () => {
    if (!isConnected || !execution.sessionId) return;

    try {
      const response = await fetch(`http://localhost:8000/api/v1/agents/execution/${execution.sessionId}/status`);
      if (response.ok) {
        const data = await response.json();
        
        setExecution(prev => ({
          ...prev,
          isRunning: data.isRunning ?? false,
          isPaused: data.isPaused ?? false,
          currentAgent: data.currentAgent,
          currentStep: data.currentStep,
          progress: data.progress ?? {},
          statuses: data.statuses ?? {},
          results: data.results ?? {},
          errors: data.errors ?? {},
          estimatedCompletion: data.estimatedCompletion,
          completedSteps: data.completedSteps ?? 0
        }));

        // Update individual agent statuses with enhanced metrics
        setAgents(prev => prev.map(agent => ({
          ...agent,
          status: data.statuses?.[agent.id] ?? agent.status,
          progress: data.progress?.[agent.id],
          lastUpdate: data.lastUpdate ?? new Date().toISOString(),
          error: data.errors?.[agent.id],
          metrics: {
            ...agent.metrics,
            ...data.metrics?.[agent.id]
          }
        })));

        // Update system metrics
        if (data.systemMetrics) {
          setSystemMetrics(prev => ({
            ...prev,
            ...data.systemMetrics
          }));
        }
      }
    } catch (error) {
      console.error('Failed to fetch agent status:', error);
      // Set agents to error state if unable to fetch status
      setAgents(prev => prev.map(agent => ({
        ...agent,
        status: agent.status === 'processing' ? 'error' : agent.status,
        error: 'Connection lost during execution'
      })));
    }
  }, [isConnected, execution.sessionId]);

  // Start intelligent agent workflow execution
  const startExecution = async (query: string = "Analyze uploaded data", options: any = {}) => {
    if (!isConnected) {
      console.error('Backend not connected - cannot start execution');
      return;
    }

    try {
      const sessionId = execution.sessionId ?? `session_${Date.now()}_${Math.random().toString(36).substring(2, 11)}`;
      
      const requestBody = {
        query,
        session_id: sessionId,
        agents: agents.map(a => ({
          id: a.id,
          priority: a.priority,
          dependencies: a.dependencies,
          capabilities: a.capabilities
        })),
        workflow_config: {
          sequential: true,
          retry_on_error: true,
          max_retries: 3,
          timeout_minutes: 30,
          ...options
        }
      };

      const response = await fetch('http://localhost:8000/api/v1/agents/workflow/execute', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
      });

      if (response.ok) {
        const data = await response.json();
        setExecution(prev => ({
          ...prev,
          sessionId: data.session_id ?? sessionId,
          isRunning: true,
          isPaused: false,
          startTime: Date.now(),
          totalSteps: agents.length,
          completedSteps: 0
        }));

        // Initialize all agents to waiting/queued state based on dependencies
        setAgents(prev => prev.map(agent => ({
          ...agent,
          status: agent.dependencies?.length ? 'waiting' : 'queued',
          progress: 0,
          error: undefined,
          metrics: {
            executionTime: 0,
            dataProcessed: 0,
            accuracy: 0,
            memoryUsage: 0,
            tokensUsed: 0
          }
        })));
      } else {
        throw new Error(`Failed to start execution: ${response.status}`);
      }
    } catch (error) {
      console.error('Failed to start execution:', error);
      setAgents(prev => prev.map(agent => ({
        ...agent,
        status: 'error',
        error: `Failed to start execution: ${error instanceof Error ? error.message : 'Unknown error'}`
      })));
    }
  };

  // Pause workflow execution
  const pauseExecution = async () => {
    if (!execution.sessionId || !execution.isRunning) return;

    try {
      const response = await fetch(`http://localhost:8000/api/v1/agents/execution/${execution.sessionId}/pause`, {
        method: 'POST'
      });

      if (response.ok) {
        setExecution(prev => ({
          ...prev,
          isPaused: true
        }));

        setAgents(prev => prev.map(agent => ({
          ...agent,
          status: agent.status === 'processing' ? 'paused' : agent.status
        })));
      }
    } catch (error) {
      console.error('Failed to pause execution:', error);
    }
  };

  // Resume workflow execution
  const resumeExecution = async () => {
    if (!execution.sessionId || !execution.isPaused) return;

    try {
      const response = await fetch(`http://localhost:8000/api/v1/agents/execution/${execution.sessionId}/resume`, {
        method: 'POST'
      });

      if (response.ok) {
        setExecution(prev => ({
          ...prev,
          isPaused: false
        }));

        setAgents(prev => prev.map(agent => ({
          ...agent,
          status: agent.status === 'paused' ? 'processing' : agent.status
        })));
      }
    } catch (error) {
      console.error('Failed to resume execution:', error);
    }
  };

  // Stop and terminate workflow execution
  const stopExecution = async () => {
    if (!execution.sessionId) return;

    try {
      const response = await fetch(`http://localhost:8000/api/v1/agents/execution/${execution.sessionId}/stop`, {
        method: 'POST'
      });

      if (response.ok) {
        setExecution(prev => ({
          ...prev,
          isRunning: false,
          isPaused: false
        }));

        setAgents(prev => prev.map(agent => ({
          ...agent,
          status: ['processing', 'queued', 'waiting'].includes(agent.status) ? 'idle' : agent.status
        })));
      }
    } catch (error) {
      console.error('Failed to stop execution:', error);
    }
  };

  // Reset all agents and clear workflow state
  const resetAgents = () => {
    setAgents(prev => prev.map(agent => ({
      ...agent,
      status: 'idle',
      progress: 0,
      error: undefined,
      lastUpdate: undefined,
      metrics: {
        executionTime: 0,
        dataProcessed: 0,
        accuracy: 0,
        memoryUsage: 0,
        tokensUsed: 0
      }
    })));
    
    setExecution({
      sessionId: '',
      isRunning: false,
      isPaused: false,
      progress: {},
      statuses: {},
      results: {},
      errors: {},
      totalSteps: initialAgents.length,
      completedSteps: 0
    });

    setSystemMetrics({
      activeAgents: 0,
      completedTasks: 0,
      errorRate: 0,
      avgExecutionTime: 0,
      memoryUsage: 0,
      cpuUsage: 0
    });
  };

  // Initialize and start monitoring systems
  useEffect(() => {
    checkConnection();
    
    // Create initial session with enhanced tracking
    if (!execution.sessionId) {
      const newSessionId = `session_${Date.now()}_${Math.random().toString(36).substring(2, 11)}`;
      setExecution(prev => ({
        ...prev,
        sessionId: newSessionId,
        totalSteps: initialAgents.length
      }));
    }

    const healthInterval = setInterval(checkConnection, 30000); // Check every 30s
    return () => clearInterval(healthInterval);
  }, [checkConnection]);

  // Enhanced polling for status updates with adaptive frequency
  useEffect(() => {
    if (!execution.isRunning && !execution.isPaused) return;

    const pollFrequency = execution.isRunning ? 1500 : 5000; // Faster when active
    const statusInterval = setInterval(fetchAgentStatus, pollFrequency);
    return () => clearInterval(statusInterval);
  }, [execution.isRunning, execution.isPaused, fetchAgentStatus]);

  const toggleExpanded = (agentId: string) => {
    setExpandedAgent(expandedAgent === agentId ? null : agentId);
  };

  const handleAgentCardKeyDown = (event: React.KeyboardEvent, agentId: string) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      toggleExpanded(agentId);
    }
  };

  return (
    <div className="flex flex-col gap-4">
      {/* Enhanced Control Panel */}
      <div className="backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl p-4 shadow-2xl shadow-black/25">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-3">
            <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-400 animate-pulse' : 'bg-red-400'}`} />
            <span className="text-sm font-medium text-gray-300">
              Agent System {isConnected ? 'Connected' : 'Disconnected'}
            </span>
            <div className="flex items-center gap-2 text-xs text-gray-400">
              <Activity size={12} />
              <span>{systemMetrics.activeAgents} active</span>
            </div>
          </div>
          <div className="text-xs text-gray-400">
            Session: {execution.sessionId.slice(-8)}
          </div>
        </div>

        {/* System Metrics Bar */}
        {isConnected && (
          <div className="grid grid-cols-4 gap-3 mb-3 text-xs">
            <div className="bg-white/5 rounded-lg p-2">
              <div className="text-gray-400">Tasks</div>
              <div className="text-cyan-400 font-semibold">{systemMetrics.completedTasks}</div>
            </div>
            <div className="bg-white/5 rounded-lg p-2">
              <div className="text-gray-400">Error Rate</div>
              <div className="text-amber-400 font-semibold">{systemMetrics.errorRate.toFixed(1)}%</div>
            </div>
            <div className="bg-white/5 rounded-lg p-2">
              <div className="text-gray-400">Avg Time</div>
              <div className="text-green-400 font-semibold">{systemMetrics.avgExecutionTime.toFixed(1)}s</div>
            </div>
            <div className="bg-white/5 rounded-lg p-2">
              <div className="text-gray-400">Memory</div>
              <div className="text-purple-400 font-semibold">{systemMetrics.memoryUsage.toFixed(1)}%</div>
            </div>
          </div>
        )}
        
        <div className="flex gap-2">
          <button
            onClick={() => startExecution()}
            disabled={execution.isRunning || !isConnected}
            className="flex items-center gap-2 px-4 py-2 bg-cyan-500/20 border border-cyan-500/30 rounded-lg text-cyan-400 text-sm font-medium hover:bg-cyan-500/30 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300"
          >
            <Play size={16} />
            {execution.isRunning ? 'Running...' : 'Start Analysis'}
          </button>
          
          {execution.isRunning && !execution.isPaused && (
            <button
              onClick={pauseExecution}
              className="flex items-center gap-2 px-4 py-2 bg-purple-500/20 border border-purple-500/30 rounded-lg text-purple-400 text-sm font-medium hover:bg-purple-500/30 transition-all duration-300"
            >
              <Square size={16} />
              Pause
            </button>
          )}

          {execution.isPaused && (
            <button
              onClick={resumeExecution}
              className="flex items-center gap-2 px-4 py-2 bg-green-500/20 border border-green-500/30 rounded-lg text-green-400 text-sm font-medium hover:bg-green-500/30 transition-all duration-300"
            >
              <Play size={16} />
              Resume
            </button>
          )}
          
          <button
            onClick={stopExecution}
            disabled={!execution.isRunning && !execution.isPaused}
            className="flex items-center gap-2 px-4 py-2 bg-red-500/20 border border-red-500/30 rounded-lg text-red-400 text-sm font-medium hover:bg-red-500/30 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300"
          >
            <Square size={16} />
            Stop
          </button>
          
          <button
            onClick={resetAgents}
            disabled={execution.isRunning || execution.isPaused}
            className="flex items-center gap-2 px-4 py-2 bg-gray-500/20 border border-gray-500/30 rounded-lg text-gray-400 text-sm font-medium hover:bg-gray-500/30 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300"
          >
            <RotateCcw size={16} />
            Reset
          </button>
        </div>

        {/* Progress Overview */}
        {(execution.isRunning || execution.isPaused) && (
          <div className="mt-3 p-3 bg-white/5 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-300">Workflow Progress</span>
              <span className="text-xs text-gray-400">
                {execution.completedSteps}/{execution.totalSteps} steps
              </span>
            </div>
            <div className="w-full h-2 bg-white/10 rounded-full overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-cyan-500 to-blue-500 transition-all duration-500"
                style={{ width: `${((execution.completedSteps ?? 0) / (execution.totalSteps ?? 1)) * 100}%` }}
              />
            </div>
          </div>
        )}
      </div>

      {/* Enhanced Agent List */}
      <div className="flex flex-col gap-3">
        {agents.map((agent, index) => (
          <div key={agent.id} className="relative">
            {/* Main Agent Card */}
            <div
              role="button"
              tabIndex={0}
              aria-expanded={expandedAgent === agent.id}
              aria-label={`${agent.name} - ${getStatusText(agent.status, agent.progress)}`}
              className={`
                backdrop-blur-md border rounded-2xl p-4 
                transition-all duration-300 cursor-pointer 
                hover:transform hover:scale-[1.02] hover:shadow-2xl
                group relative overflow-hidden focus:outline-none focus:ring-2 focus:ring-cyan-400/50
                ${getStatusColor(agent.status)}
              `}
              onClick={() => toggleExpanded(agent.id)}
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
                  {execution.currentAgent === agent.id && execution.currentStep && (
                    <div className="text-xs text-cyan-400 bg-cyan-400/10 px-2 py-1 rounded">
                      {execution.currentStep}
                    </div>
                  )}
                  
                  <ChevronDown 
                    className={`w-5 h-5 text-gray-400 group-hover:text-gray-300 transition-all duration-300 ${
                      expandedAgent === agent.id ? 'rotate-180' : ''
                    }`} 
                  />
                </div>
              </div>                {/* Enhanced Metrics Display */}
                {agent.metrics && (execution.isRunning || execution.isPaused || agent.status === 'complete') && (
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
            </div>

            {/* Enhanced Expanded Details */}
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
                      {agent.dependencies.map(dep => (
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
                {execution.results[agent.id] && (
                  <div className="mb-3">
                    <div className="text-sm font-medium text-gray-300 mb-2">Execution Results:</div>
                    <div className="bg-white/5 rounded-lg p-3 max-h-40 overflow-y-auto">
                      <pre className="text-xs text-gray-400 whitespace-pre-wrap">
                        {JSON.stringify(execution.results[agent.id], null, 2)}
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

      {/* Enhanced Workflow Execution Info */}
      {(execution.isRunning || execution.isPaused) && (
        <div className="backdrop-blur-md bg-white/5 border border-white/10 rounded-xl p-4 shadow-lg">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-3">
              <span className="text-sm font-medium text-gray-300">
                Workflow Status: {execution.isPaused ? 'Paused' : 'Executing'}
              </span>
              {execution.currentAgent && (
                <span className="text-xs bg-cyan-500/20 text-cyan-400 px-2 py-1 rounded">
                  Current: {agents.find(a => a.id === execution.currentAgent)?.name ?? execution.currentAgent}
                </span>
              )}
            </div>
            <div className="flex items-center gap-2 text-xs text-gray-400">
              <div className={`w-2 h-2 rounded-full ${execution.isPaused ? 'bg-purple-400' : 'bg-cyan-400 animate-pulse'}`} />
              <span>
                {execution.startTime ? 
                  `Running for ${Math.round((Date.now() - execution.startTime) / 1000)}s` : 
                  'Starting...'
                }
              </span>
              {execution.estimatedCompletion && (
                <span className="ml-2">
                  ETA: {Math.round((execution.estimatedCompletion - Date.now()) / 1000)}s
                </span>
              )}
            </div>
          </div>

          {/* Current Step Information */}
          {execution.currentStep && (
            <div className="text-xs text-gray-400 bg-white/5 rounded p-2 mb-3">
              <span className="font-medium">Current Step: </span>
              <span>{execution.currentStep}</span>
            </div>
          )}

          {/* Workflow Steps Progress */}
          <div className="grid grid-cols-4 gap-2">
            {agents.map((agent, index) => (
              <div key={agent.id} className="flex flex-col items-center gap-1">
                <div className={`w-8 h-8 rounded-full border-2 flex items-center justify-center text-xs font-bold transition-all duration-300 ${getWorkflowStepStyle(agent.status)}`}>
                  {index + 1}
                </div>
                <span className="text-xs text-gray-400 text-center">{agent.name.split(' ')[0]}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* System Status Footer */}
      {!isConnected && (
        <div className="backdrop-blur-md bg-red-500/10 border border-red-500/30 rounded-xl p-3 shadow-lg">
          <div className="flex items-center gap-2 text-red-400">
            <AlertCircle size={16} />
            <span className="text-sm font-medium">System Offline</span>
          </div>
          <p className="text-xs text-gray-400 mt-1">
            Backend connection lost. Please check if the server is running on localhost:8000
          </p>
        </div>
      )}
    </div>
  );
}
