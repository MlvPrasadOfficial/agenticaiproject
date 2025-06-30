'use client';

import React, { useState } from 'react';
import { Play, Square, RotateCcw, Loader2, CheckCircle, AlertCircle, Clock } from 'lucide-react';
import { useExecuteAgent, useExecutionStatus } from '@/hooks/api';

interface Agent {
  id: string;
  name: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
  status: 'idle' | 'processing' | 'active' | 'complete';
  color: string;
  gradient: string;
}

interface AgentExecutorProps {
  agent: Agent;
  onStatusChange?: (agentId: string, status: Agent['status']) => void;
  className?: string;
}

export default function AgentExecutor({ agent, onStatusChange, className = '' }: AgentExecutorProps) {
  const [executionId, setExecutionId] = useState<string | null>(null);
  const [isExecuting, setIsExecuting] = useState(false);

  const executeAgent = useExecuteAgent();
  const { data: executionStatus } = useExecutionStatus(executionId ?? '', !!executionId);

  const handleExecute = () => {
    if (isExecuting) return;

    setIsExecuting(true);
    onStatusChange?.(agent.id, 'processing');

    executeAgent.mutate({
      agent_type: agent.id,
      query: `Execute ${agent.name} analysis`,
      parameters: {
        mode: 'interactive',
        depth: 'comprehensive'
      }
    }, {
      onSuccess: (response) => {
        setExecutionId(response.execution_id);
        // Status will be updated via polling
      },
      onError: () => {
        setIsExecuting(false);
        onStatusChange?.(agent.id, 'idle');
      }
    });
  };

  const handleStop = () => {
    setIsExecuting(false);
    setExecutionId(null);
    onStatusChange?.(agent.id, 'idle');
  };

  const handleReset = () => {
    setIsExecuting(false);
    setExecutionId(null);
    onStatusChange?.(agent.id, 'idle');
  };

  // Update status based on execution response
  React.useEffect(() => {
    if (executionStatus) {
      const status = executionStatus.status;
      if (status === 'completed') {
        setIsExecuting(false);
        onStatusChange?.(agent.id, 'complete');
      } else if (status === 'failed') {
        setIsExecuting(false);
        onStatusChange?.(agent.id, 'idle');
      } else if (status === 'running' || status === 'pending') {
        onStatusChange?.(agent.id, 'processing');
      }
    }
  }, [executionStatus, agent.id, onStatusChange]);

  const getStatusIcon = () => {
    if (executeAgent.isPending) {
      return <Loader2 className="w-4 h-4 animate-spin text-blue-400" />;
    }

    switch (agent.status) {
      case 'processing':
        return <Loader2 className="w-4 h-4 animate-spin text-blue-400" />;
      case 'complete':
        return <CheckCircle className="w-4 h-4 text-green-400" />;
      case 'active':
        return <Play className="w-4 h-4 text-green-400" />;
      default:
        return <Clock className="w-4 h-4 text-gray-400" />;
    }
  };

  const getStatusText = () => {
    if (executeAgent.isPending) return 'Starting...';
    
    switch (agent.status) {
      case 'processing':
        return executionStatus?.progress ? `${executionStatus.progress}% complete` : 'Processing...';
      case 'complete':
        return 'Completed';
      case 'active':
        return 'Active';
      default:
        return 'Ready';
    }
  };

  const getProgressWidth = () => {
    if (agent.status === 'complete') return '100%';
    if (agent.status === 'processing' && executionStatus?.progress) {
      return `${executionStatus.progress}%`;
    }
    return '0%';
  };

  return (
    <div className={`space-y-3 ${className}`}>
      {/* Status Bar */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          {getStatusIcon()}
          <span className="text-slate-400 text-xs uppercase tracking-wide">
            {getStatusText()}
          </span>
        </div>
        
        {typeof executionStatus?.progress === 'number' && agent.status === 'processing' && (
          <span className="text-xs text-slate-500">
            ~{Math.round((executionStatus.progress ?? 0) / 100 * 30)}s remaining
          </span>
        )}
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-gray-700 rounded-full h-1.5 overflow-hidden">
        <div 
          className="h-full bg-gradient-to-r from-blue-500 to-purple-600 transition-all duration-500 ease-out"
          style={{ width: getProgressWidth() }}
        />
      </div>

      {/* Control Buttons */}
      <div className="flex space-x-2">
        {agent.status === 'idle' || agent.status === 'complete' ? (
          <button
            onClick={handleExecute}
            disabled={executeAgent.isPending}
            className="flex-1 flex items-center justify-center space-x-1 px-3 py-2 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 disabled:from-gray-600 disabled:to-gray-700 disabled:cursor-not-allowed text-white rounded-lg transition-all duration-200 text-xs font-medium"
          >
            <Play className="w-3 h-3" />
            <span>Execute</span>
          </button>
        ) : (
          <button
            onClick={handleStop}
            className="flex-1 flex items-center justify-center space-x-1 px-3 py-2 bg-gradient-to-r from-red-600 to-pink-600 hover:from-red-700 hover:to-pink-700 text-white rounded-lg transition-all duration-200 text-xs font-medium"
          >
            <Square className="w-3 h-3" />
            <span>Stop</span>
          </button>
        )}
        
        {agent.status !== 'idle' && (
          <button
            onClick={handleReset}
            className="px-3 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-all duration-200 text-xs"
          >
            <RotateCcw className="w-3 h-3" />
          </button>
        )}
      </div>

      {/* Execution Results */}
      {executionStatus?.result && agent.status === 'complete' && (
        <div className="mt-3 p-3 bg-white/5 rounded-lg border border-white/10">
          <h5 className="text-xs font-semibold text-white mb-2">Results:</h5>
          <div className="text-xs text-slate-300 space-y-1">
            {executionStatus.result.insights?.map((insight: string, index: number) => (
              <div key={index} className="flex items-start space-x-2">
                <span className="text-green-400">•</span>
                <span>{insight}</span>
              </div>
            ))}
            {executionStatus.result.summary && (
              <p className="mt-2 italic text-slate-400">{executionStatus.result.summary}</p>
            )}
          </div>
        </div>
      )}

      {/* Error Display */}
      {executeAgent.isError && (
        <div className="mt-3 p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
          <div className="flex items-center space-x-2 text-red-400">
            <AlertCircle className="w-4 h-4" />
            <span className="text-xs font-medium">Execution Failed</span>
          </div>
          <p className="text-xs text-red-300 mt-1">
            {executeAgent.error?.message || 'An unexpected error occurred'}
          </p>
        </div>
      )}
    </div>
  );
}
