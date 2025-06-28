'use client';

import React, { useState, useEffect, useRef } from 'react';
import { 
  Send, 
  Mic, 
  Upload, 
  Settings, 
  History, 
  Download,
  Share2,
  Bot,
  User,
  Lightbulb,
  BarChart3
} from 'lucide-react';
import VoiceInput from '@/components/VoiceInput';
import ConversationHistory, { ConversationMessage } from '@/components/ConversationHistory';
import ResultsVisualization, { AnalysisResult } from '@/components/ResultsVisualization';
import InsightCards, { Insight } from '@/components/InsightCards';
import ExportSharing, { ExportData } from '@/components/ExportSharing';

export default function ConversationPage() {
  const [messages, setMessages] = useState<ConversationMessage[]>([]);
  const [results, setResults] = useState<AnalysisResult[]>([]);
  const [insights, setInsights] = useState<Insight[]>([]);
  const [inputText, setInputText] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'chat' | 'results' | 'insights'>('chat');
  const [showExportModal, setShowExportModal] = useState(false);
  const [exportData, setExportData] = useState<ExportData | null>(null);
  const [isVoiceEnabled, setIsVoiceEnabled] = useState(false);
  
  const inputRef = useRef<HTMLInputElement>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);

  // Initialize session
  useEffect(() => {
    initializeSession();
  }, []);

  const initializeSession = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/agents/session', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: 'demo-user',
          session_name: `Conversation ${new Date().toLocaleString()}`
        }),
      });
      
      if (response.ok) {
        const session = await response.json();
        setSessionId(session.session_id);
        
        // Add welcome message
        setMessages([{
          id: 'welcome',
          type: 'system',
          content: 'Welcome to Enterprise Insights Copilot! I can help you analyze data, generate insights, and answer questions. What would you like to explore today?',
          timestamp: new Date()
        }]);
      }
    } catch (error) {
      console.error('Failed to initialize session:', error);
    }
  };

  const handleSendMessage = async () => {
    if (!inputText.trim() || !sessionId || isProcessing) return;

    const userMessage: ConversationMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: inputText.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsProcessing(true);

    try {
      // Execute agent
      const response = await fetch('http://localhost:8000/api/v1/agents/execute', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          agent_type: 'planning',
          query: userMessage.content,
          session_id: sessionId
        }),
      });

      if (response.ok) {
        const execution = await response.json();
        
        // Add assistant response
        const assistantMessage: ConversationMessage = {
          id: execution.execution_id,
          type: 'assistant',
          content: execution.result?.response || 'I\'m processing your request. Let me analyze this for you.',
          timestamp: new Date(),
          metadata: {
            agentType: 'planning',
            executionId: execution.execution_id,
            processingTime: execution.processing_time
          }
        };

        setMessages(prev => [...prev, assistantMessage]);

        // Generate mock results and insights for demo
        if (execution.result) {
          generateMockResults(userMessage.content);
          generateMockInsights(userMessage.content);
        }
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      const errorMessage: ConversationMessage = {
        id: `error-${Date.now()}`,
        type: 'system',
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsProcessing(false);
    }
  };

  const generateMockResults = (query: string) => {
    const mockResult: AnalysisResult = {
      id: `result-${Date.now()}`,
      type: Math.random() > 0.5 ? 'chart' : 'metric',
      title: `Analysis of "${query.slice(0, 30)}..."`,
      description: 'Generated analysis based on your query',
      data: {
        value: Math.floor(Math.random() * 10000),
        trend: Math.random() > 0.5 ? 'up' : 'down',
        chartType: 'bar',
        data: Array.from({ length: 10 }, () => Math.floor(Math.random() * 100))
      },
      confidence: 0.7 + Math.random() * 0.3,
      timestamp: new Date(),
      metadata: {
        agentType: 'analysis',
        executionTime: Math.floor(Math.random() * 5000),
        dataSource: 'demo-data'
      }
    };

    setResults(prev => [mockResult, ...prev]);
  };

  const generateMockInsights = (query: string) => {
    const insightTypes = ['trend', 'anomaly', 'opportunity', 'success'] as const;
    const impacts = ['high', 'medium', 'low'] as const;
    
    const mockInsight: Insight = {
      id: `insight-${Date.now()}`,
      type: insightTypes[Math.floor(Math.random() * insightTypes.length)],
      title: `Key insight from "${query.slice(0, 20)}..."`,
      description: 'This analysis reveals important patterns in your data that could impact your business decisions.',
      impact: impacts[Math.floor(Math.random() * impacts.length)],
      confidence: 0.6 + Math.random() * 0.4,
      priority: Math.floor(Math.random() * 100),
      timestamp: new Date(),
      data: {
        value: Math.floor(Math.random() * 1000),
        change: (Math.random() - 0.5) * 50,
        recommendations: [
          'Consider implementing automated monitoring for this metric',
          'Review historical data to identify patterns',
          'Set up alerts for significant changes'
        ]
      },
      tags: ['analysis', 'data-driven', 'actionable'],
      isRead: false,
      isPinned: false
    };

    setInsights(prev => [mockInsight, ...prev]);
  };

  const handleVoiceTranscript = (transcript: string) => {
    setInputText(transcript);
    inputRef.current?.focus();
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleExport = async (format: string, options: any) => {
    // Mock export functionality
    console.log('Exporting:', format, options);
    
    // Simulate export delay
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // In a real implementation, this would trigger a download
    const blob = new Blob(['Mock export data'], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `export.${format}`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleShare = async (method: string, options: any) => {
    // Mock sharing functionality
    console.log('Sharing:', method, options);
    
    // Simulate sharing delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    if (method === 'link') {
      const mockUrl = `https://insights.example.com/shared/${Date.now()}`;
      await navigator.clipboard.writeText(mockUrl);
    }
  };

  const openExportModal = (type: ExportData['type']) => {
    let data: any;
    let title: string;
    
    switch (type) {
      case 'conversation':
        data = messages;
        title = 'Conversation History';
        break;
      case 'analysis':
        data = results;
        title = 'Analysis Results';
        break;
      case 'insight':
        data = insights;
        title = 'Generated Insights';
        break;
      default:
        data = {};
        title = 'Export Data';
    }

    setExportData({
      type,
      title,
      data,
      metadata: {
        timestamp: new Date(),
        sessionId: sessionId || undefined
      }
    });
    setShowExportModal(true);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto p-6">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Enterprise Insights Copilot</h1>
              <p className="text-gray-600 mt-1">
                AI-powered conversation and analysis platform
              </p>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={() => setIsVoiceEnabled(!isVoiceEnabled)}
                className={`p-2 rounded-lg transition-colors ${
                  isVoiceEnabled 
                    ? 'bg-blue-100 text-blue-600' 
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
                title="Toggle voice input"
              >
                <Mic className="w-5 h-5" />
              </button>
              <button
                onClick={() => openExportModal('conversation')}
                className="p-2 bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200 transition-colors"
                title="Export conversation"
              >
                <Download className="w-5 h-5" />
              </button>
              <button
                className="p-2 bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200 transition-colors"
                title="Share"
              >
                <Share2 className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-6">
          <div className="flex border-b border-gray-200">
            <button
              onClick={() => setActiveTab('chat')}
              className={`flex items-center gap-2 px-6 py-3 text-sm font-medium transition-colors ${
                activeTab === 'chat'
                  ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <Bot className="w-4 h-4" />
              Conversation ({messages.length})
            </button>
            <button
              onClick={() => setActiveTab('results')}
              className={`flex items-center gap-2 px-6 py-3 text-sm font-medium transition-colors ${
                activeTab === 'results'
                  ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <BarChart3 className="w-4 h-4" />
              Results ({results.length})
            </button>
            <button
              onClick={() => setActiveTab('insights')}
              className={`flex items-center gap-2 px-6 py-3 text-sm font-medium transition-colors ${
                activeTab === 'insights'
                  ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <Lightbulb className="w-4 h-4" />
              Insights ({insights.filter(i => !i.isRead).length})
            </button>
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {activeTab === 'chat' && (
              <div className="space-y-6">
                {/* Conversation History */}
                <div 
                  ref={chatContainerRef}
                  className="bg-gray-50 rounded-lg border border-gray-200 max-h-96 overflow-y-auto"
                >
                  <ConversationHistory
                    messages={messages}
                    onMessageCopy={(content) => {
                      navigator.clipboard.writeText(content);
                    }}
                    className="p-4"
                  />
                </div>

                {/* Input Area */}
                <div className="bg-white border border-gray-200 rounded-lg p-4">
                  <div className="flex items-end gap-4">
                    <div className="flex-1">
                      <input
                        ref={inputRef}
                        type="text"
                        value={inputText}
                        onChange={(e) => setInputText(e.target.value)}
                        onKeyPress={handleKeyPress}
                        placeholder="Ask me anything about your data or request an analysis..."
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                        disabled={isProcessing}
                      />
                    </div>
                    
                    {isVoiceEnabled && (
                      <VoiceInput
                        onTranscript={handleVoiceTranscript}
                        disabled={isProcessing}
                      />
                    )}
                    
                    <button
                      onClick={handleSendMessage}
                      disabled={!inputText.trim() || isProcessing}
                      className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
                    >
                      {isProcessing ? (
                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      ) : (
                        <Send className="w-4 h-4" />
                      )}
                      Send
                    </button>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'results' && (
              <div>
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold text-gray-900">Analysis Results</h2>
                  <button
                    onClick={() => openExportModal('analysis')}
                    className="flex items-center gap-2 px-3 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    <Download className="w-4 h-4" />
                    Export Results
                  </button>
                </div>
                <ResultsVisualization
                  results={results}
                  onResultSelect={(result) => console.log('Selected result:', result)}
                  onExport={(result) => {
                    setExportData({
                      type: 'analysis',
                      title: result.title,
                      data: result,
                      metadata: {
                        timestamp: new Date(),
                        sessionId: sessionId || undefined
                      }
                    });
                    setShowExportModal(true);
                  }}
                />
              </div>
            )}

            {activeTab === 'insights' && (
              <div>
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold text-gray-900">Generated Insights</h2>
                  <button
                    onClick={() => openExportModal('insight')}
                    className="flex items-center gap-2 px-3 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    <Download className="w-4 h-4" />
                    Export Insights
                  </button>
                </div>
                <InsightCards
                  insights={insights}
                  onInsightClick={(insight) => console.log('Selected insight:', insight)}
                  onInsightPin={(id) => {
                    setInsights(prev => prev.map(i => 
                      i.id === id ? { ...i, isPinned: !i.isPinned } : i
                    ));
                  }}
                  onInsightDismiss={(id) => {
                    setInsights(prev => prev.filter(i => i.id !== id));
                  }}
                  onInsightMarkRead={(id) => {
                    setInsights(prev => prev.map(i => 
                      i.id === id ? { ...i, isRead: true } : i
                    ));
                  }}
                />
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Export Modal */}
      {showExportModal && exportData && (
        <ExportSharing
          data={exportData}
          onExport={handleExport}
          onShare={handleShare}
          isOpen={showExportModal}
          onClose={() => setShowExportModal(false)}
        />
      )}
    </div>
  );
}
