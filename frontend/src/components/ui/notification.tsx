'use client';

import React, { createContext, useContext, useState, useCallback, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { createPortal } from 'react-dom';
import { X, CheckCircle, AlertCircle, AlertTriangle, Info, Loader2 } from 'lucide-react';

interface Notification {
  id: string;
  title: string;
  message?: string;
  type: 'success' | 'error' | 'warning' | 'info' | 'loading';
  duration?: number;
  actions?: NotificationAction[];
  dismissible?: boolean;
  persistent?: boolean;
  icon?: React.ReactNode;
}

interface NotificationAction {
  label: string;
  onClick: () => void;
  variant?: 'primary' | 'secondary' | 'danger';
}

interface NotificationContextType {
  notifications: Notification[];
  addNotification: (notification: Omit<Notification, 'id'>) => string;
  removeNotification: (id: string) => void;
  updateNotification: (id: string, updates: Partial<Notification>) => void;
  clearAll: () => void;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

export function useNotifications() {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications must be used within a NotificationProvider');
  }
  return context;
}

// Alias for compatibility with WebSocket hooks
export const useNotification = useNotifications;

interface NotificationProviderProps {
  children: React.ReactNode;
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left' | 'top-center' | 'bottom-center';
  maxNotifications?: number;
}

export function NotificationProvider({ 
  children, 
  position = 'top-right',
  maxNotifications = 5 
}: NotificationProviderProps) {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const timeoutsRef = useRef<Map<string, NodeJS.Timeout>>(new Map());

  const addNotification = useCallback((notification: Omit<Notification, 'id'>) => {
    const id = Math.random().toString(36).substr(2, 9);
    const newNotification: Notification = {
      id,
      duration: 5000,
      dismissible: true,
      persistent: false,
      ...notification
    };

    setNotifications(prev => {
      const updated = [newNotification, ...prev];
      // Limit the number of notifications
      if (updated.length > maxNotifications) {
        const removed = updated.slice(maxNotifications);
        removed.forEach(n => {
          const timeout = timeoutsRef.current.get(n.id);
          if (timeout) {
            clearTimeout(timeout);
            timeoutsRef.current.delete(n.id);
          }
        });
        return updated.slice(0, maxNotifications);
      }
      return updated;
    });

    // Auto-dismiss if not persistent and has duration
    if (!newNotification.persistent && newNotification.duration && newNotification.duration > 0) {
      const timeout = setTimeout(() => {
        removeNotification(id);
      }, newNotification.duration);
      timeoutsRef.current.set(id, timeout);
    }

    return id;
  }, [maxNotifications]);

  const removeNotification = useCallback((id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
    const timeout = timeoutsRef.current.get(id);
    if (timeout) {
      clearTimeout(timeout);
      timeoutsRef.current.delete(id);
    }
  }, []);

  const updateNotification = useCallback((id: string, updates: Partial<Notification>) => {
    setNotifications(prev => 
      prev.map(n => n.id === id ? { ...n, ...updates } : n)
    );
  }, []);

  const clearAll = useCallback(() => {
    timeoutsRef.current.forEach(timeout => clearTimeout(timeout));
    timeoutsRef.current.clear();
    setNotifications([]);
  }, []);

  // Clean up timeouts on unmount
  useEffect(() => {
    return () => {
      timeoutsRef.current.forEach(timeout => clearTimeout(timeout));
    };
  }, []);

  const contextValue: NotificationContextType = {
    notifications,
    addNotification,
    removeNotification,
    updateNotification,
    clearAll
  };

  const getPositionClasses = () => {
    const positions = {
      'top-right': 'top-4 right-4',
      'top-left': 'top-4 left-4',
      'bottom-right': 'bottom-4 right-4',
      'bottom-left': 'bottom-4 left-4',
      'top-center': 'top-4 left-1/2 transform -translate-x-1/2',
      'bottom-center': 'bottom-4 left-1/2 transform -translate-x-1/2'
    };
    return positions[position];
  };

  return (
    <NotificationContext.Provider value={contextValue}>
      {children}
      {typeof window !== 'undefined' && createPortal(
        <div className={`fixed z-[9999] ${getPositionClasses()} max-w-sm w-full`}>
          <AnimatePresence mode="popLayout">
            {notifications.map((notification, index) => (
              <NotificationItem
                key={notification.id}
                notification={notification}
                onRemove={removeNotification}
                index={index}
                position={position}
              />
            ))}
          </AnimatePresence>
        </div>,
        document.body
      )}
    </NotificationContext.Provider>
  );
}

interface NotificationItemProps {
  notification: Notification;
  onRemove: (id: string) => void;
  index: number;
  position: string;
}

function NotificationItem({ notification, onRemove, index, position }: NotificationItemProps) {
  const [isHovered, setIsHovered] = useState(false);

  const getIcon = () => {
    if (notification.icon) return notification.icon;
    
    const icons = {
      success: <CheckCircle className="w-5 h-5 text-green-500" />,
      error: <AlertCircle className="w-5 h-5 text-red-500" />,
      warning: <AlertTriangle className="w-5 h-5 text-amber-500" />,
      info: <Info className="w-5 h-5 text-blue-500" />,
      loading: <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />
    };
    
    return icons[notification.type];
  };

  const getTypeClasses = () => {
    const types = {
      success: 'border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-900/20',
      error: 'border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-900/20',
      warning: 'border-amber-200 bg-amber-50 dark:border-amber-800 dark:bg-amber-900/20',
      info: 'border-blue-200 bg-blue-50 dark:border-blue-800 dark:bg-blue-900/20',
      loading: 'border-blue-200 bg-blue-50 dark:border-blue-800 dark:bg-blue-900/20'
    };
    return types[notification.type];
  };

  const getSlideDirection = () => {
    if (position.includes('right')) return { x: 400 };
    if (position.includes('left')) return { x: -400 };
    return { y: position.includes('top') ? -100 : 100 };
  };

  const getActionButtonClasses = (variant: NotificationAction['variant'] = 'secondary') => {
    const variants = {
      primary: 'bg-blue-600 hover:bg-blue-700 text-white',
      secondary: 'bg-gray-100 hover:bg-gray-200 text-gray-700 dark:bg-gray-700 dark:hover:bg-gray-600 dark:text-gray-300',
      danger: 'bg-red-600 hover:bg-red-700 text-white'
    };
    return variants[variant];
  };

  return (
    <motion.div
      layout
      initial={getSlideDirection()}
      animate={{ x: 0, y: 0 }}
      exit={getSlideDirection()}
      transition={{ 
        type: 'spring', 
        stiffness: 400, 
        damping: 30,
        layout: { duration: 0.2 }
      }}
      role={notification.type === 'error' || notification.type === 'warning' ? 'alert' : 'status'}
      aria-live={notification.type === 'error' ? 'assertive' : 'polite'}
      aria-atomic="true"
      aria-label={`${notification.type} notification: ${notification.title}`}
      className={`
        mb-4 relative overflow-hidden rounded-lg border backdrop-blur-sm
        shadow-lg transition-all duration-200 focus-within:ring-2 focus-within:ring-primary
        ${getTypeClasses()}
        ${isHovered ? 'shadow-xl scale-105' : ''}
      `}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      style={{ zIndex: 9999 - index }}
    >
      <div className="p-4">
        <div className="flex items-start gap-3">
          <div className="flex-shrink-0 mt-0.5">
            {getIcon()}
          </div>
          
          <div className="flex-1 min-w-0">
            <h4 className="text-sm font-semibold text-gray-900 dark:text-gray-100 mb-1">
              {notification.title}
            </h4>
            
            {notification.message && (
              <p className="text-sm text-gray-600 dark:text-gray-300 mb-3">
                {notification.message}
              </p>
            )}
            
            {notification.actions && notification.actions.length > 0 && (
              <div className="flex gap-2 mt-3" role="group" aria-label="Notification actions">
                {notification.actions.map((action, actionIndex) => (
                  <button
                    key={actionIndex}
                    onClick={action.onClick}
                    className={`
                      px-3 py-1.5 text-xs font-medium rounded
                      transition-colors duration-200 focus:ring-2 focus:ring-primary focus:ring-offset-1 focus:outline-none
                      ${getActionButtonClasses(action.variant)}
                    `}
                  >
                    {action.label}
                  </button>
                ))}
              </div>
            )}
          </div>
          
          {notification.dismissible && (
            <button
              onClick={() => onRemove(notification.id)}
              className="flex-shrink-0 p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors duration-200 focus:ring-2 focus:ring-primary focus:ring-offset-1 focus:outline-none"
              aria-label={`Dismiss ${notification.type} notification: ${notification.title}`}
            >
              <X className="w-4 h-4 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300" aria-hidden="true" />
            </button>
          )}
        </div>
      </div>
      
      {/* Progress bar for timed notifications */}
      {!notification.persistent && notification.duration && notification.duration > 0 && (
        <motion.div
          className="absolute bottom-0 left-0 h-1 bg-current opacity-20"
          initial={{ width: '100%' }}
          animate={{ width: '0%' }}
          transition={{ duration: notification.duration / 1000, ease: 'linear' }}
        />
      )}
    </motion.div>
  );
}

// Utility hooks for common notification patterns
export function useToast() {
  const { addNotification } = useNotifications();

  const toast = useCallback((message: string, type: Notification['type'] = 'info') => {
    return addNotification({
      title: message,
      type,
      duration: 4000
    });
  }, [addNotification]);

  const success = useCallback((message: string, options?: Partial<Notification>) => {
    return addNotification({
      title: message,
      type: 'success',
      duration: 4000,
      ...options
    });
  }, [addNotification]);

  const error = useCallback((message: string, options?: Partial<Notification>) => {
    return addNotification({
      title: message,
      type: 'error',
      duration: 6000,
      ...options
    });
  }, [addNotification]);

  const warning = useCallback((message: string, options?: Partial<Notification>) => {
    return addNotification({
      title: message,
      type: 'warning',
      duration: 5000,
      ...options
    });
  }, [addNotification]);

  const info = useCallback((message: string, options?: Partial<Notification>) => {
    return addNotification({
      title: message,
      type: 'info',
      duration: 4000,
      ...options
    });
  }, [addNotification]);

  const loading = useCallback((message: string, options?: Partial<Notification>) => {
    return addNotification({
      title: message,
      type: 'loading',
      persistent: true,
      dismissible: false,
      ...options
    });
  }, [addNotification]);

  return {
    toast,
    success,
    error,
    warning,
    info,
    loading
  };
}

// Simple notification function for quick use
export function showNotification(
  title: string,
  type: Notification['type'] = 'info',
  options?: Partial<Notification>
) {
  // This would need to be used within the provider context
  console.warn('showNotification should be used within NotificationProvider context. Use useToast hook instead.');
}
