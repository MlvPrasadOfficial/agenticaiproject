'use client';

import React, { useState, useCallback } from 'react';
import { 
  Upload, Target, Lightbulb, Brain, FileText, 
  Database, Search, Zap, Check, Play, Loader2, AlertCircle
} from 'lucide-react';

// Import UI components
import FileUploadQueue from './ui/file-upload-queue';
import ChatInterface from './ChatInterface';

// Types
interface Agent {
  id: string;
  name: string;
  description: string;
  subtitle: string;
  icon: React.ComponentType<{ className?: string }>;
  status: 'idle' | 'processing' | 'active' | 'complete' | 'disabled';
  color: string;
  glowClass: string;
  gradientFrom: string;
  gradientTo: string;
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

export default function EnhancedGlassDashboard({ className = '' }: Readonly<ModernDashboardProps>) {
  // State management
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [showNotifications, setShowNotifications] = useState(true);

  // 3 Core Agents (simplified as requested)
  const [agents, setAgents] = useState<Agent[]>([
    {
      id: 'planning',
      name: 'Planning Agent',
      subtitle: 'Strategic Analysis & Planning',
      description: 'Analyzes your requirements and creates comprehensive strategic analysis plans with actionable insights',
      icon: Target,
      status: 'idle',
      color: 'from-purple-500 to-violet-600',
      glowClass: 'planning-glow',
      gradientFrom: 'from-purple-500/20',
      gradientTo: 'to-violet-600/20'
    },
    {
      id: 'sql',
      name: 'SQL Agent',
      subtitle: 'Data Query & Extraction',
      description: 'Handles complex SQL queries, data extraction, and database operations with advanced analytics',
      icon: Database,
      status: uploadedFiles.length > 0 ? 'idle' : 'disabled',
      color: 'from-blue-500 to-cyan-600',
      glowClass: 'sql-glow',
      gradientFrom: 'from-blue-500/20',
      gradientTo: 'to-cyan-600/20'
    },
    {
      id: 'insight',
      name: 'Insight Agent',
      subtitle: 'Business Intelligence & Insights',
      description: 'Generates powerful business insights, recommendations, and actionable intelligence from your data',
      icon: Lightbulb,
      status: uploadedFiles.length > 0 ? 'idle' : 'disabled',
      color: 'from-amber-500 to-orange-600',
      glowClass: 'insight-glow',
      gradientFrom: 'from-amber-500/20',
      gradientTo: 'to-orange-600/20'
    }
  ]);

  // Handlers
  const handleUploadComplete = useCallback((files: any[]) => {
    const newFiles: UploadedFile[] = files.map(file => ({
      id: crypto.randomUUID(),
      name: file.file?.name ?? 'Unknown',
      size: file.file?.size ?? 0,
      type: file.file?.type ?? 'Unknown',
      uploadedAt: new Date(),
      fileId: file.id // Backend file ID for API calls
    }));
    
    setUploadedFiles(prev => [...prev, ...newFiles]);
    
    // Enable agents when files are uploaded
    setAgents(prev => prev.map(agent => 
      agent.id !== 'planning' ? { ...agent, status: 'idle' } : agent
    ));
  }, []);

  const handleUploadError = useCallback((error: string) => {
    console.error('Upload error:', error);
  }, []);

  const handleAgentStatusChange = useCallback((agentId: string, status: Agent['status']) => {
    setAgents(prev => prev.map(agent => 
      agent.id === agentId ? { ...agent, status } : agent
    ));
  }, []);

  const handleExecuteAgent = useCallback((agent: Agent) => {
    if (agent.status === 'disabled') return;
    
    setSelectedAgent(agent);
    handleAgentStatusChange(agent.id, 'processing');
    
    // Simulate processing
    setTimeout(() => {
      handleAgentStatusChange(agent.id, 'complete');
    }, 3000);
  }, [handleAgentStatusChange]);

  const getStatusIcon = (status: Agent['status']) => {
    switch (status) {
      case 'processing': return <Loader2 className="w-4 h-4 animate-spin" />;
      case 'complete': return <Check className="w-4 h-4" />;
      case 'disabled': return <AlertCircle className="w-4 h-4 opacity-50" />;
      default: return <Play className="w-4 h-4" />;
    }
  };

  const getStatusColor = (status: Agent['status']) => {
    switch (status) {
      case 'processing': return 'status-processing';
      case 'complete': return 'status-ready';
      case 'disabled': return 'status-disabled';
      default: return 'bg-white/20 hover:bg-white/30';
    }
  };

  const getButtonText = (status: Agent['status']) => {
    switch (status) {
      case 'processing': return 'Processing...';
      case 'complete': return 'Completed';
      case 'disabled': return 'Upload Data First';
      default: return 'Execute Agent';
    }
  };

  return (
    <div className={`min-h-screen bg-black relative overflow-hidden ${className}`}>
      {/* Enhanced Background with Multiple Layers */}
      <div className="absolute inset-0">
        {/* Base grid pattern */}
        <div className="absolute inset-0 opacity-[0.03]" style={{
          backgroundImage: `radial-gradient(circle at 2px 2px, rgba(255, 255, 255, 0.15) 1px, transparent 0)`,
          backgroundSize: '80px 80px'
        }} />
        
        {/* Animated ambient lighting */}
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl animate-pulse" style={{animationDelay: '2s'}} />
        <div className="absolute top-1/2 right-1/3 w-64 h-64 bg-amber-500/8 rounded-full blur-3xl animate-pulse" style={{animationDelay: '4s'}} />
      </div>

      {/* Main Content */}
      <div className="relative z-10 min-h-screen flex flex-col">
        {/* Enhanced Header with Glassmorphism */}
        <header className="glass-card border-b border-white/10 sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-6 lg:px-8">
            <div className="flex items-center justify-between h-20">
              {/* Enhanced Logo with Glowing Effect */}
              <div className="flex items-center space-x-4">
                <div className="relative">
                  <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center floating-icon shadow-lg">
                    <Brain className="w-6 h-6 text-white" />
                  </div>
                  <div className="absolute inset-0 bg-gradient-to-br from-blue-400 to-purple-500 rounded-xl blur-md opacity-50 -z-10"></div>
                </div>
                <div>
                  <h1 className="text-xl font-bold gradient-text">
                    Enterprise Insights
                  </h1>
                  <p className="text-xs text-slate-400">AI-Powered Intelligence Platform</p>
                </div>
              </div>

              {/* Enhanced Search with Glassmorphism */}
              <div className="relative max-w-sm">
                <input
                  type="text"
                  placeholder="Search agents..."
                  className="w-full px-4 py-3 pl-11 glass-card text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all duration-300 rounded-xl"
                />
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              </div>
            </div>
          </div>
        </header>

        {/* Main Content Area */}
        <main className="flex-1 max-w-7xl mx-auto px-6 lg:px-8 py-8 w-full">
          <div className="space-y-12">
            {/* Hero Section with Enhanced Typography */}
            <div className="text-center space-y-4">
              <h2 className="text-4xl md:text-5xl font-bold gradient-text leading-tight">
                AI-Powered Business Intelligence
              </h2>
              <p className="text-slate-400 max-w-3xl mx-auto text-lg leading-relaxed">
                Upload your data and let our intelligent agents analyze, process, and generate actionable insights with enterprise-grade AI technology
              </p>
            </div>

            {/* Enhanced Upload Section - Single Large Card */}
            <div className="max-w-4xl mx-auto">
              <div className="upload-cta glass-card p-8 md:p-12">
                <div className="text-center mb-8">
                  <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl mb-6 floating-icon">
                    <Upload className="w-10 h-10 text-white" />
                  </div>
                  <h3 className="text-2xl md:text-3xl font-bold text-white mb-3">Upload Your Data</h3>
                  <p className="text-slate-300 text-lg">Drop files here or click to browse • CSV, Excel, JSON supported</p>
                </div>

                <FileUploadQueue
                  onUploadComplete={handleUploadComplete}
                  onUploadError={handleUploadError}
                  className="mb-8"
                />

                {/* Enhanced Uploaded Files Display */}
                {uploadedFiles.length > 0 && (
                  <div className="glass-card p-6 border border-white/20">
                    <div className="flex items-center justify-between mb-6">
                      <h4 className="text-lg font-semibold text-white flex items-center">
                        <FileText className="w-5 h-5 mr-2 text-blue-400" />
                        Uploaded Files
                      </h4>
                      <span className="text-sm text-slate-400 bg-white/10 px-3 py-1 rounded-full">
                        {uploadedFiles.length} file{uploadedFiles.length !== 1 ? 's' : ''}
                      </span>
                    </div>
                    <div className="grid gap-4">
                      {uploadedFiles.map((file) => (
                        <div key={file.id} className="glass-card p-4 border border-white/10 hover:border-white/20 transition-all duration-300">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-4 flex-1 min-w-0">
                              <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-emerald-600 rounded-lg flex items-center justify-center flex-shrink-0">
                                <FileText className="w-5 h-5 text-white" />
                              </div>
                              <div className="flex-1 min-w-0">
                                <span className="text-white text-base font-medium block truncate">{file.name}</span>
                                <div className="flex items-center space-x-3 text-sm text-slate-400 mt-1">
                                  <span>{(file.size / 1024 / 1024).toFixed(2)} MB</span>
                                  <span>•</span>
                                  <span>{file.type}</span>
                                  <span>•</span>
                                  <span>{file.uploadedAt.toLocaleDateString()}</span>
                                </div>
                              </div>
                            </div>
                            <div className="flex items-center space-x-3">
                              <button className="glass-button text-sm">
                                Preview
                              </button>
                              <button className="glass-button text-sm bg-gradient-to-r from-green-500/20 to-emerald-500/20 border-green-500/30">
                                Analyze
                              </button>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Enhanced AI Agent Ecosystem - 3 Cards */}
            <div className="space-y-8">
              <div className="text-center">
                <h3 className="text-3xl font-bold gradient-text mb-3">AI Agent Ecosystem</h3>
                <p className="text-slate-300 text-lg">Three specialized agents working together to analyze your data</p>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
                {agents.map((agent) => {
                  const IconComponent = agent.icon;
                  const isDisabled = agent.status === 'disabled';
                  
                  return (
                    <button
                      key={agent.id}
                      onClick={() => !isDisabled && handleExecuteAgent(agent)}
                      onKeyDown={(e) => {
                        if ((e.key === 'Enter' || e.key === ' ') && !isDisabled) {
                          e.preventDefault();
                          handleExecuteAgent(agent);
                        }
                      }}
                      className={`agent-card-3d glass-card p-8 h-80 cursor-pointer transition-all duration-500 ${agent.glowClass} ${
                        isDisabled ? 'opacity-60 cursor-not-allowed' : 'hover:scale-[1.02]'
                      } w-full text-left border-0`}
                      disabled={isDisabled}
                      aria-label={`Execute ${agent.name}`}
                    >
                      {/* Enhanced Background Gradient */}
                      <div className={`absolute inset-0 bg-gradient-to-br ${agent.gradientFrom} ${agent.gradientTo} opacity-0 hover:opacity-30 transition-opacity duration-500 rounded-2xl`} />
                      
                      {/* Content */}
                      <div className="relative z-10 h-full flex flex-col">
                        {/* Enhanced Agent Icon */}
                        <div className="relative mb-6">
                          <div className={`w-16 h-16 bg-gradient-to-br ${agent.color} rounded-2xl flex items-center justify-center floating-icon shadow-2xl`}>
                            <IconComponent className="w-8 h-8 text-white" />
                          </div>
                          <div className={`absolute inset-0 bg-gradient-to-br ${agent.color} rounded-2xl blur-lg opacity-50 -z-10`}></div>
                        </div>

                        {/* Enhanced Agent Info */}
                        <div className="flex-1 mb-6">
                          <h4 className="text-xl font-bold text-white mb-2">
                            {agent.name}
                          </h4>
                          <p className="text-sm font-medium text-blue-200 mb-3">
                            {agent.subtitle}
                          </p>
                          <p className="text-slate-300 text-sm leading-relaxed">
                            {agent.description}
                          </p>
                        </div>

                        {/* Enhanced Execute Button */}
                        <div className="mt-auto">
                          <button 
                            className={`w-full py-3 px-6 rounded-xl font-semibold transition-all duration-300 flex items-center justify-center space-x-2 ${getStatusColor(agent.status)}`}
                            disabled={isDisabled}
                          >
                            {getStatusIcon(agent.status)}
                            <span>{getButtonText(agent.status)}</span>
                          </button>
                        </div>
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Enhanced Metrics with Glassmorphism */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
              <div className="glass-card p-6 hover:scale-105 transition-all duration-300">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-slate-400 text-sm uppercase tracking-wide font-medium">Total Files</p>
                    <p className="text-3xl font-bold text-white mt-2">{uploadedFiles.length}</p>
                  </div>
                  <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl flex items-center justify-center floating-icon">
                    <FileText className="w-6 h-6 text-white" />
                  </div>
                </div>
              </div>

              <div className="glass-card p-6 hover:scale-105 transition-all duration-300">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-slate-400 text-sm uppercase tracking-wide font-medium">Data Points</p>
                    <p className="text-3xl font-bold text-white mt-2">2.4M</p>
                  </div>
                  <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center floating-icon">
                    <Database className="w-6 h-6 text-white" />
                  </div>
                </div>
              </div>

              <div className="glass-card p-6 hover:scale-105 transition-all duration-300">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-slate-400 text-sm uppercase tracking-wide font-medium">AI Insights</p>
                    <p className="text-3xl font-bold text-white mt-2">127</p>
                  </div>
                  <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-violet-600 rounded-xl flex items-center justify-center floating-icon">
                    <Zap className="w-6 h-6 text-white" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </main>

        {/* Enhanced Glassy Footer */}
        {showNotifications && (
          <div className="footer-glass p-4">
            <div className="max-w-7xl mx-auto flex items-center justify-between">
              <div className="flex items-center space-x-6">
                <div className="flex items-center space-x-2 text-sm text-slate-300">
                  <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                  <span>System Online</span>
                </div>
                <div className="flex items-center space-x-2 text-sm text-slate-400">
                  <Zap className="w-4 h-4" />
                  <span>AI Ready</span>
                </div>
              </div>
              <button 
                onClick={() => setShowNotifications(false)}
                className="text-slate-400 hover:text-white transition-colors"
              >
                ✕
              </button>
            </div>
          </div>
        )}

        {/* Chat Interface - Enhanced */}
        {selectedAgent && (
          <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="glass-card max-w-4xl w-full max-h-[80vh] overflow-hidden">
              <ChatInterface 
                selectedAgent={selectedAgent} 
                onClose={() => setSelectedAgent(null)}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
