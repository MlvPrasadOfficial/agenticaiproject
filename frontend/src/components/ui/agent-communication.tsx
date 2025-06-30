'use client';

import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Bot, User, AlertCircle, CheckCircle, Clock, Send, MoreVertical, Copy, Trash2 } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

interface Message {
  id: string;
  content: string;
  type: 'user' | 'agent' | 'system' | 'error';
  timestamp: Date;
  agentId?: string;
  agentName?: string;
  status?: 'sending' | 'sent' | 'delivered' | 'error';
  metadata?: {
    executionTime?: number;
    tokens?: number;
    model?: string;
    confidence?: number;
  };
  attachments?: MessageAttachment[];
  reactions?: MessageReaction[];
}

interface MessageAttachment {
  id: string;
  name: string;
  type: 'file' | 'image' | 'chart' | 'data';
  url: string;
  size?: number;
}

interface MessageReaction {
  emoji: string;
  count: number;
  userReacted: boolean;
}

interface AgentCommunicationProps {
  messages: Message[];
  onSendMessage?: (content: string) => void;
  onDeleteMessage?: (messageId: string) => void;
  onCopyMessage?: (content: string) => void;
  onReactToMessage?: (messageId: string, emoji: string) => void;
  currentUserId?: string;
  isLoading?: boolean;
  className?: string;
  showTypingIndicator?: boolean;
  typingAgents?: string[];
}

export function AgentCommunication({
  messages,
  onSendMessage,
  onDeleteMessage,
  onCopyMessage,
  onReactToMessage,
  currentUserId = 'user',
  isLoading = false,
  className = '',
  showTypingIndicator = false,
  typingAgents = []
}: AgentCommunicationProps) {
  const [newMessage, setNewMessage] = useState('');
  const [selectedMessage, setSelectedMessage] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = () => {
    if (!newMessage.trim() || isLoading) return;
    
    onSendMessage?.(newMessage.trim());
    setNewMessage('');
    inputRef.current?.focus();
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const getMessageIcon = (message: Message) => {
    switch (message.type) {
      case 'user':
        return <User className="w-4 h-4" />;
      case 'agent':
        return <Bot className="w-4 h-4" />;
      case 'system':
        return <AlertCircle className="w-4 h-4" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      default:
        return <Bot className="w-4 h-4" />;
    }
  };

  const getMessageStatusIcon = (status: Message['status']) => {
    switch (status) {
      case 'sending':
        return <Clock className="w-3 h-3 text-gray-400 animate-pulse" />;
      case 'sent':
      case 'delivered':
        return <CheckCircle className="w-3 h-3 text-green-500" />;
      case 'error':
        return <AlertCircle className="w-3 h-3 text-red-500" />;
      default:
        return null;
    }
  };

  const getMessageBubbleClasses = (message: Message) => {
    const isUser = message.type === 'user';
    const baseClasses = `
      max-w-[80%] rounded-2xl px-4 py-3 shadow-sm
      transition-all duration-200 hover:shadow-md
    `;

    if (isUser) {
      return `${baseClasses} bg-blue-500 text-white ml-auto`;
    }

    switch (message.type) {
      case 'agent':
        return `${baseClasses} bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100`;
      case 'system':
        return `${baseClasses} bg-amber-50 dark:bg-amber-900/20 text-amber-800 dark:text-amber-200 border border-amber-200 dark:border-amber-800`;
      case 'error':
        return `${baseClasses} bg-red-50 dark:bg-red-900/20 text-red-800 dark:text-red-200 border border-red-200 dark:border-red-800`;
      default:
        return `${baseClasses} bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100`;
    }
  };

  const renderMessageMetadata = (message: Message) => {
    if (!message.metadata) return null;

    const { executionTime, tokens, model, confidence } = message.metadata;

    return (
      <div className="text-xs text-gray-500 dark:text-gray-400 mt-2 space-y-1">
        {executionTime && <div>⏱️ {executionTime}ms</div>}
        {tokens && <div>🔤 {tokens} tokens</div>}
        {model && <div>🤖 {model}</div>}
        {confidence && <div>📊 {Math.round(confidence * 100)}% confidence</div>}
      </div>
    );
  };

  const renderAttachments = (attachments: MessageAttachment[]) => {
    return (
      <div className="mt-2 space-y-2">
        {attachments.map(attachment => (
          <div
            key={attachment.id}
            className="flex items-center gap-2 p-2 bg-gray-50 dark:bg-gray-700 rounded-lg text-sm"
          >
            <div className="w-8 h-8 bg-blue-100 dark:bg-blue-900 rounded flex items-center justify-center">
              📎
            </div>
            <div className="flex-1">
              <div className="font-medium">{attachment.name}</div>
              {attachment.size && (
                <div className="text-xs text-gray-500">
                  {(attachment.size / 1024).toFixed(1)} KB
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderReactions = (reactions: MessageReaction[], messageId: string) => {
    if (!reactions.length) return null;

    return (
      <div className="flex gap-1 mt-2">
        {reactions.map(reaction => (
          <button
            key={reaction.emoji}
            onClick={() => onReactToMessage?.(messageId, reaction.emoji)}
            className={`
              px-2 py-1 text-xs rounded-full border transition-colors
              ${reaction.userReacted
                ? 'bg-blue-100 dark:bg-blue-900 border-blue-300 dark:border-blue-700'
                : 'bg-gray-100 dark:bg-gray-700 border-gray-300 dark:border-gray-600 hover:bg-gray-200 dark:hover:bg-gray-600'
              }
            `}
          >
            {reaction.emoji} {reaction.count}
          </button>
        ))}
      </div>
    );
  };

  const renderTypingIndicator = () => {
    if (!showTypingIndicator || !typingAgents.length) return null;

    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        className="flex items-center gap-3 px-4 py-2"
      >
        <div className="w-8 h-8 bg-gray-200 dark:bg-gray-700 rounded-full flex items-center justify-center">
          <Bot className="w-4 h-4" />
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-600 dark:text-gray-400">
            {typingAgents.join(', ')} {typingAgents.length === 1 ? 'is' : 'are'} typing
          </span>
          <div className="flex gap-1">
            {[0, 1, 2].map(i => (
              <motion.div
                key={i}
                className="w-1.5 h-1.5 bg-gray-400 rounded-full"
                animate={{ scale: [1, 1.2, 1] }}
                transition={{
                  duration: 1,
                  repeat: Infinity,
                  delay: i * 0.2
                }}
              />
            ))}
          </div>
        </div>
      </motion.div>
    );
  };

  return (
    <div className={`flex flex-col h-full bg-white dark:bg-gray-900 ${className}`}>
      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <AnimatePresence>
          {messages.map((message, index) => {
            const isUser = message.type === 'user';
            const showAvatar = index === 0 || messages[index - 1].type !== message.type;

            return (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 20, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -20, scale: 0.95 }}
                transition={{ duration: 0.2 }}
                className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
              >
                {/* Avatar */}
                {showAvatar && (
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                    isUser ? 'bg-blue-500 text-white' : 'bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-300'
                  }`}>
                    {getMessageIcon(message)}
                  </div>
                )}

                {/* Message Content */}
                <div className={`flex flex-col ${isUser ? 'items-end' : 'items-start'} ${!showAvatar ? 'ml-11' : ''}`}>
                  {/* Agent Name and Timestamp */}
                  {!isUser && showAvatar && (
                    <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                      {message.agentName || `Agent ${message.agentId}`}
                    </div>
                  )}

                  {/* Message Bubble */}
                  <div className="group relative">
                    <div
                      className={getMessageBubbleClasses(message)}
                      onClick={() => setSelectedMessage(selectedMessage === message.id ? null : message.id)}
                    >
                      <div className="break-words">{message.content}</div>
                      
                      {/* Attachments */}
                      {message.attachments && renderAttachments(message.attachments)}
                      
                      {/* Metadata */}
                      {renderMessageMetadata(message)}
                    </div>

                    {/* Message Actions */}
                    {selectedMessage === message.id && (
                      <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className={`absolute top-0 ${isUser ? 'right-full mr-2' : 'left-full ml-2'} bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 p-1 flex gap-1`}
                      >
                        <button
                          onClick={() => onCopyMessage?.(message.content)}
                          className="p-1.5 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors"
                          title="Copy message"
                        >
                          <Copy className="w-4 h-4" />
                        </button>
                        {onDeleteMessage && (
                          <button
                            onClick={() => onDeleteMessage(message.id)}
                            className="p-1.5 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors text-red-500"
                            title="Delete message"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        )}
                      </motion.div>
                    )}
                  </div>

                  {/* Reactions */}
                  {message.reactions && renderReactions(message.reactions, message.id)}

                  {/* Timestamp and Status */}
                  <div className={`flex items-center gap-2 mt-1 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
                    <span className="text-xs text-gray-500 dark:text-gray-400">
                      {formatDistanceToNow(message.timestamp, { addSuffix: true })}
                    </span>
                    {message.status && getMessageStatusIcon(message.status)}
                  </div>
                </div>
              </motion.div>
            );
          })}
        </AnimatePresence>

        {/* Typing Indicator */}
        <AnimatePresence>
          {renderTypingIndicator()}
        </AnimatePresence>

        <div ref={messagesEndRef} />
      </div>

      {/* Message Input */}
      <div className="border-t border-gray-200 dark:border-gray-700 p-4">
        <div className="flex gap-3 items-end">
          <div className="flex-1 relative">
            <textarea
              ref={inputRef}
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message..."
              disabled={isLoading}
              className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-xl resize-none bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent max-h-32"
              rows={1}
              style={{
                minHeight: '48px',
                height: 'auto'
              }}
            />
          </div>
          
          <button
            onClick={handleSendMessage}
            disabled={!newMessage.trim() || isLoading}
            className="p-3 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-300 dark:disabled:bg-gray-600 text-white rounded-xl transition-colors duration-200 disabled:cursor-not-allowed"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}

// Hook for managing agent communication state
export function useAgentCommunication(initialMessages: Message[] = []) {
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [isLoading, setIsLoading] = useState(false);
  const [typingAgents, setTypingAgents] = useState<string[]>([]);

  const addMessage = (message: Omit<Message, 'id' | 'timestamp'>) => {
    const newMessage: Message = {
      ...message,
      id: Math.random().toString(36).substr(2, 9),
      timestamp: new Date()
    };
    setMessages(prev => [...prev, newMessage]);
    return newMessage.id;
  };

  const updateMessage = (messageId: string, updates: Partial<Message>) => {
    setMessages(prev =>
      prev.map(msg => msg.id === messageId ? { ...msg, ...updates } : msg)
    );
  };

  const deleteMessage = (messageId: string) => {
    setMessages(prev => prev.filter(msg => msg.id !== messageId));
  };

  const addAgentTyping = (agentName: string) => {
    setTypingAgents(prev => [...new Set([...prev, agentName])]);
  };

  const removeAgentTyping = (agentName: string) => {
    setTypingAgents(prev => prev.filter(name => name !== agentName));
  };

  const clearMessages = () => {
    setMessages([]);
  };

  return {
    messages,
    addMessage,
    updateMessage,
    deleteMessage,
    clearMessages,
    isLoading,
    setIsLoading,
    typingAgents,
    addAgentTyping,
    removeAgentTyping
  };
}
