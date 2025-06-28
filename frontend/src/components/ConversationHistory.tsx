'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Bot, User, Clock, Copy, ThumbsUp, ThumbsDown, MoreVertical, Trash2, Edit3 } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

interface ConversationMessage {
  id: string;
  type: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  metadata?: {
    agentType?: string;
    executionId?: string;
    processingTime?: number;
    confidence?: number;
  };
  feedback?: {
    rating: 'positive' | 'negative';
    comment?: string;
  };
}

interface ConversationHistoryProps {
  messages: ConversationMessage[];
  onMessageEdit?: (messageId: string, newContent: string) => void;
  onMessageDelete?: (messageId: string) => void;
  onMessageFeedback?: (messageId: string, feedback: ConversationMessage['feedback']) => void;
  onMessageCopy?: (content: string) => void;
  className?: string;
  autoScroll?: boolean;
}

export default function ConversationHistory({
  messages,
  onMessageEdit,
  onMessageDelete,
  onMessageFeedback,
  onMessageCopy,
  className = '',
  autoScroll = true
}: ConversationHistoryProps) {
  const [editingMessageId, setEditingMessageId] = useState<string | null>(null);
  const [editContent, setEditContent] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (autoScroll && messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, autoScroll]);

  const handleEdit = (messageId: string, content: string) => {
    setEditingMessageId(messageId);
    setEditContent(content);
  };

  const saveEdit = () => {
    if (editingMessageId && onMessageEdit) {
      onMessageEdit(editingMessageId, editContent);
      setEditingMessageId(null);
      setEditContent('');
    }
  };

  const cancelEdit = () => {
    setEditingMessageId(null);
    setEditContent('');
  };

  const copyToClipboard = async (content: string) => {
    try {
      await navigator.clipboard.writeText(content);
      onMessageCopy?.(content);
    } catch (error) {
      console.error('Failed to copy text:', error);
    }
  };

  const getMessageIcon = (type: string, metadata?: ConversationMessage['metadata']) => {
    switch (type) {
      case 'user':
        return <User className="w-5 h-5 text-blue-600" />;
      case 'assistant':
        return <Bot className="w-5 h-5 text-green-600" />;
      case 'system':
        return <Clock className="w-5 h-5 text-gray-500" />;
      default:
        return <Bot className="w-5 h-5 text-gray-500" />;
    }
  };

  const getMessageBgColor = (type: string) => {
    switch (type) {
      case 'user':
        return 'bg-blue-50 border-blue-200';
      case 'assistant':
        return 'bg-green-50 border-green-200';
      case 'system':
        return 'bg-gray-50 border-gray-200';
      default:
        return 'bg-white border-gray-200';
    }
  };

  if (messages.length === 0) {
    return (
      <div className={`flex flex-col items-center justify-center py-12 text-gray-500 ${className}`}>
        <Bot className="w-12 h-12 mb-4 text-gray-300" />
        <h3 className="text-lg font-medium mb-2">No conversation yet</h3>
        <p className="text-sm text-center max-w-md">
          Start a conversation by typing a message or using voice input to interact with the AI assistant.
        </p>
      </div>
    );
  }

  return (
    <div 
      ref={containerRef}
      className={`flex flex-col space-y-4 p-4 max-h-96 overflow-y-auto scroll-smooth ${className}`}
    >
      {messages.map((message, index) => (
        <div key={message.id} className="flex flex-col">
          <div className={`flex gap-3 p-4 rounded-lg border ${getMessageBgColor(message.type)}`}>
            <div className="flex-shrink-0 mt-1">
              {getMessageIcon(message.type, message.metadata)}
            </div>

            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className="font-medium text-gray-900 capitalize">
                    {message.type === 'assistant' && message.metadata?.agentType 
                      ? `${message.metadata.agentType} Agent`
                      : message.type
                    }
                  </span>
                  <span className="text-xs text-gray-500">
                    {formatDistanceToNow(message.timestamp, { addSuffix: true })}
                  </span>
                  {message.metadata?.processingTime && (
                    <span className="text-xs text-gray-400">
                      ({message.metadata.processingTime}ms)
                    </span>
                  )}
                </div>

                <div className="flex items-center gap-1">
                  <button
                    onClick={() => copyToClipboard(message.content)}
                    className="p-1 hover:bg-white/80 rounded transition-colors"
                    title="Copy message"
                  >
                    <Copy className="w-4 h-4 text-gray-400 hover:text-gray-600" />
                  </button>
                  
                  {onMessageEdit && message.type === 'user' && (
                    <button
                      onClick={() => handleEdit(message.id, message.content)}
                      className="p-1 hover:bg-white/80 rounded transition-colors"
                      title="Edit message"
                    >
                      <Edit3 className="w-4 h-4 text-gray-400 hover:text-gray-600" />
                    </button>
                  )}
                  
                  {onMessageDelete && (
                    <button
                      onClick={() => onMessageDelete(message.id)}
                      className="p-1 hover:bg-white/80 rounded transition-colors"
                      title="Delete message"
                    >
                      <Trash2 className="w-4 h-4 text-gray-400 hover:text-red-600" />
                    </button>
                  )}
                </div>
              </div>

              {editingMessageId === message.id ? (
                <div className="space-y-2">
                  <textarea
                    value={editContent}
                    onChange={(e) => setEditContent(e.target.value)}
                    className="w-full p-2 border border-gray-300 rounded-md resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    rows={3}
                    autoFocus
                  />
                  <div className="flex gap-2">
                    <button
                      onClick={saveEdit}
                      className="px-3 py-1 bg-blue-500 text-white text-sm rounded hover:bg-blue-600 transition-colors"
                    >
                      Save
                    </button>
                    <button
                      onClick={cancelEdit}
                      className="px-3 py-1 bg-gray-300 text-gray-700 text-sm rounded hover:bg-gray-400 transition-colors"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              ) : (
                <div className="prose prose-sm max-w-none">
                  <p className="text-gray-800 whitespace-pre-wrap">{message.content}</p>
                </div>
              )}

              {message.metadata?.confidence && (
                <div className="mt-2">
                  <div className="flex items-center gap-2 text-xs text-gray-500">
                    <span>Confidence:</span>
                    <div className="w-20 h-1 bg-gray-200 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-green-500 rounded-full transition-all duration-300"
                        style={{ width: `${message.metadata.confidence * 100}%` }}
                      />
                    </div>
                    <span>{Math.round(message.metadata.confidence * 100)}%</span>
                  </div>
                </div>
              )}

              {message.type === 'assistant' && onMessageFeedback && (
                <div className="flex items-center gap-2 mt-3 pt-3 border-t border-gray-200">
                  <span className="text-xs text-gray-500">Was this helpful?</span>
                  <button
                    onClick={() => onMessageFeedback(message.id, { rating: 'positive' })}
                    className={`p-1 rounded transition-colors ${
                      message.feedback?.rating === 'positive'
                        ? 'bg-green-100 text-green-600'
                        : 'hover:bg-gray-100 text-gray-400'
                    }`}
                    title="Thumbs up"
                  >
                    <ThumbsUp className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => onMessageFeedback(message.id, { rating: 'negative' })}
                    className={`p-1 rounded transition-colors ${
                      message.feedback?.rating === 'negative'
                        ? 'bg-red-100 text-red-600'
                        : 'hover:bg-gray-100 text-gray-400'
                    }`}
                    title="Thumbs down"
                  >
                    <ThumbsDown className="w-4 h-4" />
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      ))}
      <div ref={messagesEndRef} />
    </div>
  );
}

export type { ConversationMessage };
