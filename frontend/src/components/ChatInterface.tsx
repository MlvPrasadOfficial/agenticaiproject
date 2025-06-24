"use client";

import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2, Download, BarChart3, FileText } from 'lucide-react';
import { apiClient, type QueryRequest, type QueryResponse } from '@/lib/api';
import { downloadBlob } from '@/lib/utils';

interface Message {
  id: string;
  type: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  data?: any;
}

interface ChatInterfaceProps {
  fileId?: string;
  onInsightGenerated?: (insight: any) => void;
  onVisualizationGenerated?: (visualization: any) => void;
}

export function ChatInterface({ 
  fileId, 
  onInsightGenerated, 
  onVisualizationGenerated 
}: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'system',
      content: 'Hello! I\'m your Enterprise Insights Copilot. Upload a data file and ask me anything about your data - I can provide insights, create visualizations, and generate reports.',
      timestamp: new Date(),
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string>('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const addMessage = (message: Omit<Message, 'id' | 'timestamp'>) => {
    const newMessage: Message = {
      ...message,
      id: Date.now().toString(),
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, newMessage]);
    return newMessage;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const userMessage = inputValue.trim();
    setInputValue('');
    
    // Add user message
    addMessage({
      type: 'user',
      content: userMessage,
    });

    setIsLoading(true);

    try {
      const queryRequest: QueryRequest = {
        query: userMessage,
        file_id: fileId,
        context: { session_id: sessionId }
      };

      const response = await apiClient.processQuery(queryRequest);
      
      // Update session ID
      if (response.session_id) {
        setSessionId(response.session_id);
      }

      // Add assistant response
      const assistantMessage = addMessage({
        type: 'assistant',
        content: generateResponseText(response),
        data: response,
      });

      // Trigger callbacks for insights and visualizations
      if (response.results.insights?.length > 0) {
        response.results.insights.forEach(insight => {
          onInsightGenerated?.(insight);
        });
      }

      if (response.results.visualizations?.length > 0) {
        response.results.visualizations.forEach(viz => {
          onVisualizationGenerated?.(viz);
        });
      }

    } catch (error) {
      addMessage({
        type: 'assistant',
        content: `I apologize, but I encountered an error: ${error instanceof Error ? error.message : 'Unknown error'}. Please try again.`,
      });
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  const generateResponseText = (response: QueryResponse): string => {
    let text = `I've analyzed your query "${response.query}". Here's what I found:\n\n`;
    
    if (response.results.insights?.length > 0) {
      text += `**Key Insights:**\n`;
      response.results.insights.forEach((insight, index) => {
        text += `${index + 1}. ${insight.summary || insight.description || 'Insight generated'}\n`;
      });
      text += '\n';
    }

    if (response.results.visualizations?.length > 0) {
      text += `**Visualizations Created:** ${response.results.visualizations.length} chart(s)\n\n`;
    }

    if (response.results.sql_queries?.length > 0) {
      text += `**SQL Queries Executed:** ${response.results.sql_queries.length}\n\n`;
    }

    if (response.execution_trace?.length > 0) {
      const agents = response.execution_trace.map(trace => trace.agent).filter(Boolean);
      if (agents.length > 0) {
        text += `**AI Agents Used:** ${[...new Set(agents)].join(', ')}\n\n`;
      }
    }

    text += `You can download a detailed report or ask me follow-up questions!`;
    
    return text;
  };

  const downloadReport = async () => {
    if (!sessionId) return;
    
    try {
      const blob = await apiClient.downloadReport(sessionId, 'pdf');
      downloadBlob(blob, `insights-report-${sessionId}.pdf`);
    } catch (error) {
      console.error('Failed to download report:', error);
    }
  };

  const formatTimestamp = (date: Date): string => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="flex flex-col h-full max-h-[600px] bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center space-x-2">
          <Bot className="h-5 w-5 text-blue-600" />
          <h3 className="font-semibold text-gray-900 dark:text-gray-100">
            Enterprise Insights Copilot
          </h3>
        </div>
        {sessionId && (
          <div className="flex space-x-2">
            <button
              onClick={downloadReport}
              className="flex items-center space-x-1 px-3 py-1 text-sm text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300"
            >
              <Download className="h-4 w-4" />
              <span>Download Report</span>
            </button>
          </div>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`
                max-w-[80%] rounded-lg px-4 py-2 
                ${message.type === 'user' 
                  ? 'bg-blue-600 text-white' 
                  : message.type === 'system'
                  ? 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300'
                  : 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100'
                }
              `}
            >
              <div className="flex items-start space-x-2">
                {message.type !== 'user' && (
                  <div className="flex-shrink-0 mt-1">
                    {message.type === 'assistant' ? (
                      <Bot className="h-4 w-4" />
                    ) : (
                      <div className="h-4 w-4 rounded-full bg-gray-400" />
                    )}
                  </div>
                )}
                <div className="flex-1">
                  <div className="text-sm whitespace-pre-wrap">{message.content}</div>
                  
                  {/* Show data insights */}
                  {message.data?.results?.insights && (
                    <div className="mt-2 space-y-1">
                      {message.data.results.insights.map((insight: any, index: number) => (
                        <div key={index} className="flex items-center space-x-1 text-xs text-blue-600 dark:text-blue-400">
                          <BarChart3 className="h-3 w-3" />
                          <span>Insight {index + 1}</span>
                        </div>
                      ))}
                    </div>
                  )}
                  
                  {/* Show visualizations */}
                  {message.data?.results?.visualizations && (
                    <div className="mt-2 space-y-1">
                      {message.data.results.visualizations.map((viz: any, index: number) => (
                        <div key={index} className="flex items-center space-x-1 text-xs text-green-600 dark:text-green-400">
                          <FileText className="h-3 w-3" />
                          <span>Chart {index + 1}</span>
                        </div>
                      ))}
                    </div>
                  )}
                  
                  <div className="text-xs opacity-70 mt-1">
                    {formatTimestamp(message.timestamp)}
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 dark:bg-gray-800 rounded-lg px-4 py-2">
              <div className="flex items-center space-x-2">
                <Bot className="h-4 w-4 text-gray-600" />
                <Loader2 className="h-4 w-4 animate-spin text-gray-600" />
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  Analyzing your data...
                </span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="border-t border-gray-200 dark:border-gray-700 p-4">
        <div className="flex space-x-2">
          <input
            ref={inputRef}
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder={fileId ? "Ask anything about your data..." : "Upload a file first to start analyzing..."}
            disabled={isLoading || !fileId}
            className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-800 dark:text-gray-100 disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={isLoading || !inputValue.trim() || !fileId}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
