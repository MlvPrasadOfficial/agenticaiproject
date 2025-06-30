'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Bot, User, Send, Loader2, AlertCircle, CheckCircle } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { 
  useCreateSession, 
  useSendMessage, 
  useConversationHistory,
  useSession
} from '@/hooks/api';

interface Agent {
  id: string;
  name: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
  color: string;
}

interface ChatInterfaceProps {
  selectedAgent: Agent;
  onClose?: () => void;
  className?: string;
}

export default function ChatInterface({ selectedAgent, onClose, className = '' }: ChatInterfaceProps) {
  const [message, setMessage] = useState('');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // API hooks
  const createSession = useCreateSession();
  const sendMessage = useSendMessage();
  const { data: session } = useSession(sessionId || '', !!sessionId);
  const { data: conversationHistory = [], isLoading: historyLoading } = useConversationHistory(
    sessionId || '', 
    !!sessionId
  );

  // Create session when component mounts
  useEffect(() => {
    if (!sessionId) {
      createSession.mutate({
        session_name: `Chat with ${selectedAgent.name}`,
        metadata: { agent_type: selectedAgent.id }
      }, {
        onSuccess: (newSession) => {
          setSessionId(newSession.session_id);
        }
      });
    }
  }, [selectedAgent.id, sessionId, createSession]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [conversationHistory]);

  const handleSendMessage = () => {
    if (!message.trim() || !sessionId || sendMessage.isPending) return;

    sendMessage.mutate({
      session_id: sessionId,
      message: message.trim(),
      context: { agent_type: selectedAgent.id }
    }, {
      onSuccess: () => {
        setMessage('');
        inputRef.current?.focus();
      }
    });
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const getMessageIcon = (isUser: boolean) => {
    if (isUser) {
      return <User className="w-4 h-4 text-blue-600" />;
    }
    return <selectedAgent.icon className="w-4 h-4 text-green-600" />;
  };

  const getMessageBg = (isUser: boolean) => {
    if (isUser) {
      return 'bg-blue-50 border-blue-200 ml-12';
    }
    return 'bg-green-50 border-green-200 mr-12';
  };

  if (createSession.isPending) {
    return (
      <div className={`bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 p-6 ${className}`}>
        <div className="flex items-center justify-center h-48">
          <div className="flex items-center space-x-2 text-white">
            <Loader2 className="w-5 h-5 animate-spin" />
            <span>Starting conversation...</span>
          </div>
        </div>
      </div>
    );
  }

  if (createSession.isError) {
    return (
      <div className={`bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 p-6 ${className}`}>
        <div className="flex items-center justify-center h-48">
          <div className="flex items-center space-x-2 text-red-400">
            <AlertCircle className="w-5 h-5" />
            <span>Failed to start conversation</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 p-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className={`w-10 h-10 bg-gradient-to-br ${selectedAgent.color} rounded-lg flex items-center justify-center`}>
            <selectedAgent.icon className="w-5 h-5 text-white" />
          </div>
          <div>
            <h4 className="text-lg font-semibold text-white">{selectedAgent.name}</h4>
            <p className="text-slate-500 text-sm">
              {session ? 'Connected' : 'Connecting...'}
            </p>
          </div>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white transition-colors"
          >
            ×
          </button>
        )}
      </div>

      {/* Messages Area */}
      <div className="h-64 overflow-y-auto mb-4 space-y-3 p-2">
        {historyLoading ? (
          <div className="flex items-center justify-center h-full">
            <div className="flex items-center space-x-2 text-slate-400">
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Loading conversation...</span>
            </div>
          </div>
        ) : conversationHistory.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center text-slate-400">
              <Bot className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <p className="text-sm">Start a conversation with {selectedAgent.name}</p>
              <p className="text-xs mt-1 opacity-75">
                Ask questions about your data or request analysis
              </p>
            </div>
          </div>
        ) : (
          conversationHistory.map((msg) => (
            <div key={msg.id} className="space-y-2">
              {/* User Message */}
              <div className={`flex gap-3 p-3 rounded-lg border ${getMessageBg(true)}`}>
                <div className="flex-shrink-0 mt-1">
                  {getMessageIcon(true)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-medium text-gray-900 text-sm">You</span>
                    <span className="text-xs text-gray-500">
                      {formatDistanceToNow(new Date(msg.timestamp), { addSuffix: true })}
                    </span>
                  </div>
                  <p className="text-gray-800 text-sm whitespace-pre-wrap">{msg.message}</p>
                </div>
              </div>

              {/* Agent Response */}
              {msg.response && (
                <div className={`flex gap-3 p-3 rounded-lg border ${getMessageBg(false)}`}>
                  <div className="flex-shrink-0 mt-1">
                    {getMessageIcon(false)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-medium text-gray-900 text-sm">{selectedAgent.name}</span>
                      <span className="text-xs text-gray-500">
                        {formatDistanceToNow(new Date(msg.timestamp), { addSuffix: true })}
                      </span>
                      {msg.metadata?.confidence && (
                        <span className="text-xs text-green-600">
                          {Math.round(msg.metadata.confidence * 100)}% confident
                        </span>
                      )}
                    </div>
                    <div className="prose prose-sm max-w-none">
                      <p className="text-gray-800 text-sm whitespace-pre-wrap">{msg.response}</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))
        )}
        
        {/* Show loading when sending message */}
        {sendMessage.isPending && (
          <div className={`flex gap-3 p-3 rounded-lg border ${getMessageBg(false)}`}>
            <div className="flex-shrink-0 mt-1">
              {getMessageIcon(false)}
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <span className="font-medium text-gray-900 text-sm">{selectedAgent.name}</span>
                <span className="text-xs text-gray-500">thinking...</span>
              </div>
              <div className="flex items-center space-x-2 text-gray-600">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span className="text-sm">Processing your request...</span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="space-y-2">
        {sendMessage.isError && (
          <div className="flex items-center gap-2 text-red-400 text-sm">
            <AlertCircle className="w-4 h-4" />
            <span>Failed to send message. Please try again.</span>
          </div>
        )}
        
        <div className="flex space-x-2">
          <textarea
            ref={inputRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={`Ask ${selectedAgent.name} anything...`}
            className="flex-1 px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/50 text-sm resize-none"
            rows={2}
            disabled={sendMessage.isPending || !sessionId}
          />
          <button
            onClick={handleSendMessage}
            disabled={!message.trim() || sendMessage.isPending || !sessionId}
            className="px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 disabled:from-gray-600 disabled:to-gray-700 disabled:cursor-not-allowed text-white rounded-lg transition-all duration-200 text-sm flex items-center space-x-1"
          >
            {sendMessage.isPending ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
            <span>Send</span>
          </button>
        </div>
        
        <p className="text-xs text-slate-500 text-center">
          Press Enter to send, Shift+Enter for new line
        </p>
      </div>
    </div>
  );
}
