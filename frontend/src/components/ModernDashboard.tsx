'use client';

import React, { useState, useCallback } from 'react';
import { 
  Upload, BarChart3, Brain, MessageSquare, FileText, 
  Database, Search, Target, Lightbulb, Zap
} from 'lucide-react';

// Import UI components
import FileUploadQueue from './ui/file-upload-queue';
import ChatInterface from './ChatInterface';
import AgentExecutor from './AgentExecutor';
import { useDataPreview, useExecuteAgent } from '@/hooks/api';

// Types
interface Agent {
  id: string;
  name: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
  status: 'idle' | 'processing' | 'active' | 'complete';
  color: string;
  gradient: string;
}

interface UploadedFile {
  id: string;
  name: string;
  size: number;
  type: string;
  uploadedAt: Date;
  fileId?: string; // Backend file ID for API calls
}

interface ModernDashboardProps {
  className?: string;
}

export default function ModernDashboard({ className = '' }: Readonly<ModernDashboardProps>) {
  // State management
  const [searchQuery, setSearchQuery] = useState('');
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [agents, setAgents] = useState<Agent[]>([
    {
      id: 'planning',
      name: 'Planning Agent',
      description: 'Analyzes requirements and creates strategic analysis plans',
      icon: Target,
      status: 'idle',
      color: 'from-purple-500 to-violet-600',
      gradient: 'bg-gradient-to-br from-purple-500/20 to-violet-600/20'
    },
    {
      id: 'data',
      name: 'Data Analysis Agent',
      description: 'Processes and analyzes your data with advanced algorithms',
      icon: BarChart3,
      status: 'idle',
      color: 'from-blue-500 to-cyan-600',
      gradient: 'bg-gradient-to-br from-blue-500/20 to-cyan-600/20'
    },
    {
      id: 'query',
      name: 'Query Agent',
      description: 'Handles natural language queries and data retrieval',
      icon: MessageSquare,
      status: 'idle',
      color: 'from-green-500 to-emerald-600',
      gradient: 'bg-gradient-to-br from-green-500/20 to-emerald-600/20'
    },
    {
      id: 'insight',
      name: 'Insight Agent',
      description: 'Generates actionable insights and recommendations',
      icon: Lightbulb,
      status: 'idle',
      color: 'from-amber-500 to-orange-600',
      gradient: 'bg-gradient-to-br from-amber-500/20 to-orange-600/20'
    }
  ]);

  // Handlers
  const handleUploadComplete = useCallback((files: any[]) => {
    const newFiles: UploadedFile[] = files.map(file => ({
      id: crypto.randomUUID(),
      name: file.file?.name || 'Unknown',
      size: file.file?.size || 0,
      type: file.file?.type || 'Unknown',
      uploadedAt: new Date(),
      fileId: file.id // Backend file ID for API calls
    }));
    
    setUploadedFiles(prev => [...prev, ...newFiles]);
  }, []);

  const handleUploadError = useCallback((error: string) => {
    console.error('Upload error:', error);
  }, []);

  const handleSearch = useCallback((query: string) => {
    setSearchQuery(query);
    console.log('Searching for:', query);
  }, []);

  const handleAgentStatusChange = useCallback((agentId: string, status: Agent['status']) => {
    setAgents(prev => prev.map(agent => 
      agent.id === agentId ? { ...agent, status } : agent
    ));
  }, []);

  const handleAnalyzeFile = useCallback((fileId: string) => {
    // Find the file
    const file = uploadedFiles.find(f => f.fileId === fileId || f.id === fileId);
    if (!file) return;

    // Execute data analysis agent with file context
    const dataAgent = agents.find(a => a.id === 'data');
    if (dataAgent) {
      handleAgentStatusChange('data', 'processing');
      // The AgentExecutor will handle the actual execution
    }
  }, [uploadedFiles, agents, handleAgentStatusChange]);

  const handleAgentSelect = (agent: Agent) => {
    setSelectedAgent(agent);
  };

  const getStatusColor = (status: Agent['status']) => {
    switch (status) {
      case 'idle': return 'bg-slate-400';
      case 'processing': return 'bg-blue-400 animate-pulse';
      case 'active': return 'bg-green-400';
      case 'complete': return 'bg-purple-400';
      default: return 'bg-slate-400';
    }
  };

  return (
    <div className={`min-h-screen bg-black ${className}`}>
      {/* Minimal Background Pattern */}
      <div className="absolute inset-0 opacity-5">
        <div className="absolute inset-0" style={{
          backgroundImage: `radial-gradient(circle at 2px 2px, rgba(255, 255, 255, 0.1) 1px, transparent 0)`,
          backgroundSize: '60px 60px'
        }} />
      </div>

      {/* Subtle ambient lighting - Minimal */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-500/5 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/5 rounded-full blur-3xl" />
      </div>

      {/* Main Content - Centered Layout */}
      <div className="relative z-10 min-h-screen flex flex-col">
        {/* Header */}
        <header className="relative">
          <div className="max-w-7xl mx-auto px-6 lg:px-8">
            <div className="flex items-center justify-between h-20">
              {/* Logo and Title */}
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                  <Brain className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h1 className="text-lg font-bold text-white">
                    Enterprise Insights
                  </h1>
                </div>
              </div>

              {/* Search Bar */}
              <div className="relative max-w-sm">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => handleSearch(e.target.value)}
                  placeholder="Search agents..."
                  className="w-full px-4 py-2 pl-10 bg-gray-900 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 transition-all duration-300"
                />
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="flex-1 max-w-6xl mx-auto px-6 lg:px-8 py-6 w-full">
          <div className="space-y-8">
            {/* Hero Section */}
            <div className="text-center space-y-3">
              <h2 className="text-3xl font-bold text-white">
                AI-Powered Business Intelligence
              </h2>
              <p className="text-slate-400 max-w-2xl mx-auto">
                Upload your data and let our intelligent agents analyze, process, and generate actionable insights
              </p>
            </div>

            {/* Upload Section */}
            <div className="relative max-w-2xl mx-auto">
              {/* Upload Card */}
              <div className="relative bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 p-6">
                <div className="text-center mb-4">
                  <div className="inline-flex items-center justify-center w-12 h-12 bg-blue-600 rounded-xl mb-3">
                    <Upload className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-lg font-semibold text-white mb-1">Upload Your Data</h3>
                  <p className="text-slate-400 text-sm">Drag and drop files here or click to browse</p>
                </div>

                <FileUploadQueue
                  onUploadComplete={handleUploadComplete}
                  onUploadError={handleUploadError}
                  className="mb-6"
                />

                {uploadedFiles.length > 0 && (
                  <div className="mt-6 p-4 bg-white/5 rounded-xl border border-white/10">
                    <div className="flex items-center justify-between mb-4">
                      <h4 className="text-sm font-semibold text-white">Uploaded Files</h4>
                      <span className="text-xs text-slate-500">{uploadedFiles.length} file{uploadedFiles.length !== 1 ? 's' : ''}</span>
                    </div>
                    <div className="space-y-3">
                      {uploadedFiles.map((file) => (
                        <div key={file.id} className="flex items-center justify-between p-3 bg-white/5 rounded-lg border border-white/10">
                          <div className="flex items-center space-x-3 flex-1 min-w-0">
                            <FileText className="w-4 h-4 text-blue-400 flex-shrink-0" />
                            <div className="flex-1 min-w-0">
                              <span className="text-white text-sm font-medium block truncate">{file.name}</span>
                              <div className="flex items-center space-x-2 text-xs text-slate-500">
                                <span>{(file.size / 1024 / 1024).toFixed(2)} MB</span>
                                <span>•</span>
                                <span>{file.type}</span>
                                <span>•</span>
                                <span>{file.uploadedAt.toLocaleDateString()}</span>
                              </div>
                            </div>
                          </div>
                          <div className="flex items-center space-x-2">
                            <button 
                              onClick={() => {
                                // Open data preview (could implement modal or sidebar)
                                console.log('Preview file:', file.id);
                              }}
                              className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs transition-colors"
                            >
                              Preview
                            </button>
                            <button 
                              onClick={() => handleAnalyzeFile(file.fileId || file.id)}
                              className="px-3 py-1 bg-green-600 hover:bg-green-700 text-white rounded text-xs transition-colors"
                            >
                              Analyze
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* 4 Core Agents Section */}
            <div className="space-y-6">
              <div className="text-center">
                <h3 className="text-2xl font-bold text-white mb-2">AI Agent Ecosystem</h3>
                <p className="text-slate-400">Four specialized agents working together to analyze your data</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {agents.map((agent) => {
                  const IconComponent = agent.icon;
                  return (
                    <div
                      key={agent.id}
                      onClick={() => handleAgentSelect(agent)}
                      className="group relative cursor-pointer w-full"
                      role="button"
                      tabIndex={0}
                      aria-label={`Select ${agent.name}`}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' || e.key === ' ') {
                          e.preventDefault();
                          handleAgentSelect(agent);
                        }
                      }}
                    >
                      {/* Agent Card */}
                      <div className="relative bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 p-6 h-72 transition-all duration-300 hover:scale-[1.02] hover:shadow-2xl hover:shadow-blue-500/10 overflow-hidden">
                        {/* Background Gradient - Subtle */}
                        <div className={`absolute inset-0 ${agent.gradient} opacity-0 group-hover:opacity-50 transition-opacity duration-500`} />
                        
                        {/* Content */}
                        <div className="relative z-10 h-full flex flex-col">
                          {/* Agent Icon */}
                          <div className={`w-14 h-14 bg-gradient-to-br ${agent.color} rounded-xl flex items-center justify-center mb-4 group-hover:scale-105 transition-transform duration-300 shadow-lg`}>
                            <IconComponent className="w-7 h-7 text-white" />
                          </div>

                          {/* Agent Info */}
                          <div className="flex-1">
                            <h4 className="text-lg font-bold text-white mb-2 group-hover:text-blue-200 transition-colors duration-300">
                              {agent.name}
                            </h4>
                            <p className="text-slate-400 text-sm leading-relaxed mb-4">
                              {agent.description}
                            </p>
                          </div>

                          {/* Status */}
                          <AgentExecutor 
                            agent={agent}
                            onStatusChange={handleAgentStatusChange}
                          />
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Metrics Dashboard */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-slate-500 text-xs uppercase tracking-wide">Total Files</p>
                    <p className="text-2xl font-bold text-white mt-1">{uploadedFiles.length}</p>
                  </div>
                  <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-emerald-600 rounded-lg flex items-center justify-center">
                    <FileText className="w-5 h-5 text-white" />
                  </div>
                </div>
              </div>

              <div className="bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-slate-500 text-xs uppercase tracking-wide">Data Points</p>
                    <p className="text-2xl font-bold text-white mt-1">2.4M</p>
                  </div>
                  <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center">
                    <Database className="w-5 h-5 text-white" />
                  </div>
                </div>
              </div>

              <div className="bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-slate-500 text-xs uppercase tracking-wide">AI Insights</p>
                    <p className="text-2xl font-bold text-white mt-1">127</p>
                  </div>
                  <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-violet-600 rounded-lg flex items-center justify-center">
                    <Zap className="w-5 h-5 text-white" />
                  </div>
                </div>
              </div>
            </div>

            {/* Chat Interface */}
            {selectedAgent && (
              <div className="max-w-3xl mx-auto">
                <ChatInterface 
                  selectedAgent={selectedAgent} 
                  onClose={() => setSelectedAgent(null)}
                />
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}
