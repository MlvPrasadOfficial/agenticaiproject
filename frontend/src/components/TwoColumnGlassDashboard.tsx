'use client';

import React, { useState, useCallback } from 'react';
import { 
  Upload, Target, Lightbulb, Database, Search, Brain, FileText, 
  Send, Play, Loader2, Check, AlertCircle, MessageCircle
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
  fileId?: string;
}

interface ModernDashboardProps {
  className?: string;
}

export default function TwoColumnGlassDashboard({ className = '' }: Readonly<ModernDashboardProps>) {
  // State management
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [queryText, setQueryText] = useState('');
  const [isQueryFocused, setIsQueryFocused] = useState(false);

  // 3 Core Agents with enhanced styling
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
      fileId: file.id
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

  const handleQuerySubmit = useCallback(() => {
    if (!queryText.trim()) return;
    
    // Handle query submission
    console.log('Submitting query:', queryText);
    setQueryText('');
  }, [queryText]);

  const getStatusIcon = (status: Agent['status']) => {
    switch (status) {
      case 'processing': return <Loader2 className="w-5 h-5 animate-spin" />;
      case 'complete': return <Check className="w-5 h-5" />;
      case 'disabled': return <AlertCircle className="w-5 h-5 opacity-50" />;
      default: return <Play className="w-5 h-5" />;
    }
  };

  const getStatusColor = (status: Agent['status']) => {
    switch (status) {
      case 'processing': return 'status-processing';
      case 'complete': return 'status-ready';
      case 'disabled': return 'status-disabled';
      default: return 'bg-white/20 hover:bg-white/30 border-white/30 hover:border-white/50';
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

        {/* Hero Section with Enhanced Typography */}
        <div className="text-center space-y-4 py-12 px-6 lg:px-8">
          <h2 className="text-4xl md:text-5xl font-bold gradient-text leading-tight">
            AI-Powered Business Intelligence
          </h2>
          <p className="text-slate-400 max-w-3xl mx-auto text-lg leading-relaxed">
            Upload your data and let our intelligent agents analyze, process, and generate actionable insights with enterprise-grade AI technology
          </p>
        </div>

        {/* Main Content Area - 2 Column Layout */}
        <main className="flex-1 max-w-7xl mx-auto px-6 lg:px-8 pb-8 w-full">
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-12">
            
            {/* LEFT COLUMN - Upload & Query */}
            <div className="space-y-8">
              {/* Section Header */}
              <div className="space-y-2">
                <h3 className="text-2xl font-bold text-white flex items-center">
                  <Upload className="w-6 h-6 mr-3 text-blue-400" />
                  Upload Your Data
                </h3>
                <p className="text-slate-400 text-sm">
                  Get started by uploading your business data files
                </p>
              </div>

              {/* Single Large Upload Card */}
              <div className="upload-cta glass-card p-8">
                <div className="text-center mb-6">
                  <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl mb-4 floating-icon">
                    <Upload className="w-8 h-8 text-white" />
                  </div>
                  <h4 className="text-xl font-bold text-white mb-2">Upload Your Data</h4>
                  <p className="text-slate-300">Drop files here or click to browse</p>
                  <p className="text-sm text-slate-400 mt-1">CSV, Excel, JSON supported • Max 10MB per file</p>
                </div>

                <FileUploadQueue
                  onUploadComplete={handleUploadComplete}
                  onUploadError={handleUploadError}
                  className="mb-6"
                />

                {/* Upload Progress Indicator */}
                {uploadedFiles.length > 0 && (
                  <div className="glass-card p-4 border border-green-500/30 bg-green-500/10">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                          <Check className="w-5 h-5 text-white" />
                        </div>
                        <div>
                          <p className="text-green-400 font-medium">Upload Complete</p>
                          <p className="text-sm text-slate-400">{uploadedFiles.length} file{uploadedFiles.length !== 1 ? 's' : ''} processed</p>
                        </div>
                      </div>
                      <FileText className="w-5 h-5 text-green-400" />
                    </div>
                  </div>
                )}
              </div>

              {/* Query Copilot Input */}
              <div className="space-y-4">
                <h4 className="text-lg font-semibold text-white flex items-center">
                  <MessageCircle className="w-5 h-5 mr-2 text-purple-400" />
                  Query Copilot
                </h4>
                <div className={`relative transition-all duration-300 ${isQueryFocused ? 'scale-[1.02]' : ''}`}>
                  <div className="glass-card p-4 rounded-2xl border border-white/20 hover:border-white/30 transition-all duration-300">
                    <div className="flex items-center space-x-3">
                      <input
                        type="text"
                        value={queryText}
                        onChange={(e) => setQueryText(e.target.value)}
                        onFocus={() => setIsQueryFocused(true)}
                        onBlur={() => setIsQueryFocused(false)}
                        onKeyDown={(e) => e.key === 'Enter' && handleQuerySubmit()}
                        placeholder="Ask me anything about your data..."
                        className="flex-1 bg-transparent text-white placeholder-slate-400 outline-none text-lg"
                      />
                      <button
                        onClick={handleQuerySubmit}
                        disabled={!queryText.trim()}
                        className="w-10 h-10 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl flex items-center justify-center hover:scale-105 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
                      >
                        <Send className="w-5 h-5 text-white" />
                      </button>
                    </div>
                  </div>
                  {isQueryFocused && (
                    <div className="absolute inset-0 bg-gradient-to-r from-purple-500/20 to-pink-500/20 rounded-2xl blur-xl -z-10"></div>
                  )}
                </div>
              </div>
            </div>

            {/* RIGHT COLUMN - AI Agents */}
            <div className="space-y-8">
              {/* Section Header */}
              <div className="space-y-2">
                <h3 className="text-2xl font-bold text-white flex items-center">
                  <Brain className="w-6 h-6 mr-3 text-purple-400" />
                  AI Agent Ecosystem
                </h3>
                <p className="text-slate-400 text-sm">
                  Three specialized agents ready to analyze your data
                </p>
              </div>

              {/* Agent Cards - Vertically Stacked */}
              <div className="space-y-6">
                {agents.map((agent) => {
                  const IconComponent = agent.icon;
                  const isDisabled = agent.status === 'disabled';
                  
                  return (
                    <div
                      key={agent.id}
                      className={`agent-card-3d glass-card p-6 cursor-pointer transition-all duration-500 ${agent.glowClass} ${
                        isDisabled ? 'opacity-60' : 'hover:scale-[1.02] hover:shadow-2xl'
                      } border-0 relative overflow-hidden`}
                    >
                      {/* Enhanced Background Gradient */}
                      <div className={`absolute inset-0 bg-gradient-to-br ${agent.gradientFrom} ${agent.gradientTo} opacity-0 hover:opacity-30 transition-opacity duration-500 rounded-2xl`} />
                      
                      {/* Content */}
                      <div className="relative z-10 flex items-center space-x-6">
                        {/* Enhanced 3D Agent Icon */}
                        <div className="relative flex-shrink-0">
                          <div className={`w-16 h-16 bg-gradient-to-br ${agent.color} rounded-2xl flex items-center justify-center floating-icon shadow-2xl`}>
                            <IconComponent className="w-8 h-8 text-white" />
                          </div>
                          <div className={`absolute inset-0 bg-gradient-to-br ${agent.color} rounded-2xl blur-lg opacity-50 -z-10`}></div>
                        </div>

                        {/* Agent Info */}
                        <div className="flex-1 min-w-0">
                          <h4 className="text-xl font-bold text-white mb-1">
                            {agent.name}
                          </h4>
                          <p className="text-sm font-medium text-blue-200 mb-2">
                            {agent.subtitle}
                          </p>
                          <p className="text-slate-300 text-sm leading-relaxed">
                            {agent.description}
                          </p>
                        </div>

                        {/* Enhanced Execute Button */}
                        <div className="flex-shrink-0">
                          <button 
                            onClick={() => !isDisabled && handleExecuteAgent(agent)}
                            className={`py-3 px-6 rounded-xl font-semibold transition-all duration-300 flex items-center justify-center space-x-2 min-w-[160px] ${getStatusColor(agent.status)} border`}
                            disabled={isDisabled}
                          >
                            {getStatusIcon(agent.status)}
                            <span>{getButtonText(agent.status)}</span>
                          </button>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </main>

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
