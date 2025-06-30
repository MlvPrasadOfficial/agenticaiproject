'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Play, 
  Pause, 
  Square,
  RefreshCw,
  Wifi,
  WifiOff,
  Activity,
  Clock,
  TrendingUp,
  TrendingDown,
  Minus,
  Settings,
  Bell,
  BellOff,
  Zap
} from 'lucide-react';

interface DataUpdate {
  id: string;
  timestamp: Date;
  type: 'create' | 'update' | 'delete';
  data: any;
  previousData?: any;
  field?: string;
}

interface RealtimeDataUpdatesProps {
  isConnected: boolean;
  onConnect: () => void;
  onDisconnect: () => void;
  onDataUpdate: (update: DataUpdate) => void;
  updateInterval?: number;
  showNotifications?: boolean;
  className?: string;
}

interface UpdateStats {
  total: number;
  creates: number;
  updates: number;
  deletes: number;
  lastUpdate: Date | null;
  updatesPerMinute: number;
}

export function RealtimeDataUpdates({
  isConnected,
  onConnect,
  onDisconnect,
  onDataUpdate,
  updateInterval = 1000,
  showNotifications = true,
  className = ''
}: RealtimeDataUpdatesProps) {
  const [isActive, setIsActive] = useState(false);
  const [updates, setUpdates] = useState<DataUpdate[]>([]);
  const [stats, setStats] = useState<UpdateStats>({
    total: 0,
    creates: 0,
    updates: 0,
    deletes: 0,
    lastUpdate: null,
    updatesPerMinute: 0
  });
  const [notifications, setNotifications] = useState(true);
  const [animatingUpdates, setAnimatingUpdates] = useState<Set<string>>(new Set());
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected' | 'connecting'>('disconnected');
  
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const updatesRef = useRef<DataUpdate[]>([]);
  const lastMinuteUpdates = useRef<number[]>([]);

  // Simulate real-time updates
  const generateMockUpdate = useCallback((): DataUpdate => {
    const types = ['create', 'update', 'delete'] as const;
    const type = types[Math.floor(Math.random() * types.length)];
    
    const mockData = {
      id: Math.floor(Math.random() * 1000),
      name: `Item ${Math.floor(Math.random() * 100)}`,
      value: Math.floor(Math.random() * 1000),
      status: Math.random() > 0.5 ? 'active' : 'inactive',
      category: ['A', 'B', 'C', 'D'][Math.floor(Math.random() * 4)],
      timestamp: new Date().toISOString()
    };

    return {
      id: Date.now().toString() + Math.random(),
      timestamp: new Date(),
      type,
      data: mockData,
      previousData: type === 'update' ? { ...mockData, value: mockData.value - 10 } : undefined,
      field: type === 'update' ? ['name', 'value', 'status'][Math.floor(Math.random() * 3)] : undefined
    };
  }, []);

  // Handle real-time connection
  const startRealtime = useCallback(() => {
    setIsActive(true);
    setConnectionStatus('connecting');
    
    // Simulate connection delay
    setTimeout(() => {
      setConnectionStatus('connected');
      onConnect();
      
      intervalRef.current = setInterval(() => {
        // Generate updates with varying frequency
        const updateCount = Math.floor(Math.random() * 3) + 1; // 1-3 updates per interval
        
        for (let i = 0; i < updateCount; i++) {
          const update = generateMockUpdate();
          updatesRef.current = [update, ...updatesRef.current.slice(0, 99)]; // Keep last 100 updates
          
          setUpdates(prev => [update, ...prev.slice(0, 99)]);
          onDataUpdate(update);
          
          // Add animation
          setAnimatingUpdates(prev => new Set([...prev, update.id]));
          setTimeout(() => {
            setAnimatingUpdates(prev => {
              const newSet = new Set(prev);
              newSet.delete(update.id);
              return newSet;
            });
          }, 1000);
        }
        
        // Update stats
        setStats(prev => {
          const now = Date.now();
          lastMinuteUpdates.current = lastMinuteUpdates.current.filter(time => now - time < 60000);
          lastMinuteUpdates.current.push(now);
          
          const recentUpdates = updatesRef.current.filter(update => 
            Date.now() - update.timestamp.getTime() < 60000
          );
          
          return {
            total: updatesRef.current.length,
            creates: updatesRef.current.filter(u => u.type === 'create').length,
            updates: updatesRef.current.filter(u => u.type === 'update').length,
            deletes: updatesRef.current.filter(u => u.type === 'delete').length,
            lastUpdate: updatesRef.current[0]?.timestamp || prev.lastUpdate,
            updatesPerMinute: lastMinuteUpdates.current.length
          };
        });
      }, updateInterval);
    }, 1000);
  }, [updateInterval, onConnect, onDataUpdate, generateMockUpdate]);

  const stopRealtime = useCallback(() => {
    setIsActive(false);
    setConnectionStatus('disconnected');
    onDisconnect();
    
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, [onDisconnect]);

  const clearUpdates = () => {
    setUpdates([]);
    updatesRef.current = [];
    setStats({
      total: 0,
      creates: 0,
      updates: 0,
      deletes: 0,
      lastUpdate: null,
      updatesPerMinute: 0
    });
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  const getUpdateIcon = (type: DataUpdate['type']) => {
    switch (type) {
      case 'create':
        return <TrendingUp className="w-4 h-4 text-green-600" />;
      case 'update':
        return <RefreshCw className="w-4 h-4 text-blue-600" />;
      case 'delete':
        return <TrendingDown className="w-4 h-4 text-red-600" />;
      default:
        return <Minus className="w-4 h-4 text-gray-600" />;
    }
  };

  const getUpdateColor = (type: DataUpdate['type']) => {
    switch (type) {
      case 'create':
        return 'border-l-green-500 bg-green-50 dark:bg-green-900/20';
      case 'update':
        return 'border-l-blue-500 bg-blue-50 dark:bg-blue-900/20';
      case 'delete':
        return 'border-l-red-500 bg-red-50 dark:bg-red-900/20';
      default:
        return 'border-l-gray-500 bg-gray-50 dark:bg-gray-900/20';
    }
  };

  const formatRelativeTime = (date: Date) => {
    const diff = Date.now() - date.getTime();
    if (diff < 1000) return 'just now';
    if (diff < 60000) return `${Math.floor(diff / 1000)}s ago`;
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    return `${Math.floor(diff / 3600000)}h ago`;
  };

  return (
    <div className={`bg-white dark:bg-gray-900 rounded-xl shadow-lg overflow-hidden ${className}`}>
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Activity className="w-5 h-5 text-gray-500 dark:text-gray-400" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Real-time Updates
            </h3>
            
            {/* Connection Status */}
            <div className="flex items-center space-x-2">
              {connectionStatus === 'connected' ? (
                <div className="flex items-center space-x-1 text-green-600 dark:text-green-400">
                  <Wifi className="w-4 h-4" />
                  <span className="text-xs">Connected</span>
                </div>
              ) : connectionStatus === 'connecting' ? (
                <div className="flex items-center space-x-1 text-yellow-600 dark:text-yellow-400">
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span className="text-xs">Connecting...</span>
                </div>
              ) : (
                <div className="flex items-center space-x-1 text-gray-500 dark:text-gray-400">
                  <WifiOff className="w-4 h-4" />
                  <span className="text-xs">Disconnected</span>
                </div>
              )}
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            {/* Notifications Toggle */}
            <button
              onClick={() => setNotifications(!notifications)}
              className={`p-2 rounded-lg transition-colors ${
                notifications 
                  ? 'text-blue-600 bg-blue-100 dark:bg-blue-900/20' 
                  : 'text-gray-400 hover:text-gray-600 dark:hover:text-gray-300'
              }`}
            >
              {notifications ? <Bell className="w-4 h-4" /> : <BellOff className="w-4 h-4" />}
            </button>
            
            {/* Control Buttons */}
            {!isActive ? (
              <motion.button
                onClick={startRealtime}
                className="flex items-center space-x-2 px-3 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <Play className="w-4 h-4" />
                <span>Start</span>
              </motion.button>
            ) : (
              <motion.button
                onClick={stopRealtime}
                className="flex items-center space-x-2 px-3 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <Square className="w-4 h-4" />
                <span>Stop</span>
              </motion.button>
            )}
            
            <button
              onClick={clearUpdates}
              className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Stats */}
        <div className="mt-4 grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="text-center">
            <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats.total}</p>
            <p className="text-xs text-gray-500 dark:text-gray-400">Total Updates</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-green-600 dark:text-green-400">{stats.creates}</p>
            <p className="text-xs text-gray-500 dark:text-gray-400">Creates</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">{stats.updates}</p>
            <p className="text-xs text-gray-500 dark:text-gray-400">Updates</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-red-600 dark:text-red-400">{stats.deletes}</p>
            <p className="text-xs text-gray-500 dark:text-gray-400">Deletes</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-purple-600 dark:text-purple-400">{stats.updatesPerMinute}</p>
            <p className="text-xs text-gray-500 dark:text-gray-400">Per Minute</p>
          </div>
        </div>
      </div>

      {/* Updates Feed */}
      <div className="max-h-96 overflow-y-auto">
        <AnimatePresence>
          {updates.length === 0 ? (
            <div className="p-8 text-center text-gray-500 dark:text-gray-400">
              {isActive ? (
                <div className="flex flex-col items-center space-y-2">
                  <Zap className="w-8 h-8" />
                  <p>Waiting for updates...</p>
                </div>
              ) : (
                <div className="flex flex-col items-center space-y-2">
                  <Clock className="w-8 h-8" />
                  <p>Click "Start" to begin receiving real-time updates</p>
                </div>
              )}
            </div>
          ) : (
            <div className="divide-y divide-gray-200 dark:divide-gray-700">
              {updates.map((update, index) => (
                <motion.div
                  key={update.id}
                  initial={{ opacity: 0, x: -20, scale: 0.95 }}
                  animate={{ 
                    opacity: 1, 
                    x: 0, 
                    scale: animatingUpdates.has(update.id) ? [0.95, 1.05, 1] : 1 
                  }}
                  exit={{ opacity: 0, x: 20, scale: 0.95 }}
                  transition={{ 
                    duration: 0.3,
                    scale: { duration: 0.6, times: [0, 0.5, 1] }
                  }}
                  className={`p-4 border-l-4 ${getUpdateColor(update.type)} ${
                    animatingUpdates.has(update.id) ? 'ring-2 ring-blue-500 ring-opacity-50' : ''
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-3">
                      {getUpdateIcon(update.type)}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center space-x-2">
                          <span className="text-sm font-medium text-gray-900 dark:text-white capitalize">
                            {update.type}
                          </span>
                          {update.field && (
                            <span className="text-xs bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-400 px-2 py-0.5 rounded">
                              {update.field}
                            </span>
                          )}
                        </div>
                        
                        <div className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                          {update.type === 'create' && (
                            <span>New item: <strong>{update.data.name}</strong></span>
                          )}
                          {update.type === 'update' && (
                            <span>
                              Updated <strong>{update.data.name}</strong>
                              {update.field && update.previousData && (
                                <span className="ml-2 text-xs">
                                  ({update.previousData[update.field]} → {update.data[update.field]})
                                </span>
                              )}
                            </span>
                          )}
                          {update.type === 'delete' && (
                            <span>Deleted item: <strong>{update.data.name}</strong></span>
                          )}
                        </div>
                        
                        <div className="mt-1 text-xs text-gray-400">
                          ID: {update.data.id} • {formatRelativeTime(update.timestamp)}
                        </div>
                      </div>
                    </div>
                    
                    <div className="text-xs text-gray-400">
                      #{index + 1}
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </AnimatePresence>
      </div>

      {/* Footer */}
      {stats.lastUpdate && (
        <div className="px-6 py-3 bg-gray-50 dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
          <p className="text-xs text-gray-500 dark:text-gray-400 text-center">
            Last update: {formatRelativeTime(stats.lastUpdate)} • 
            Updates refreshed every {updateInterval}ms
          </p>
        </div>
      )}
    </div>
  );
}
