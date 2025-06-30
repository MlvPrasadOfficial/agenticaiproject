'use client';

import React, { createContext, useContext, useRef, useCallback, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Volume2, VolumeX, MessageSquare, Bell, Info, AlertTriangle, CheckCircle, XCircle } from 'lucide-react';

type AnnouncementPriority = 'polite' | 'assertive' | 'off';
type AnnouncementType = 'info' | 'success' | 'warning' | 'error' | 'navigation' | 'status';

interface Announcement {
  id: string;
  message: string;
  type: AnnouncementType;
  priority: AnnouncementPriority;
  timestamp: Date;
  persistent?: boolean;
}

interface ScreenReaderContextType {
  announce: (message: string, type?: AnnouncementType, priority?: AnnouncementPriority, persistent?: boolean) => void;
  announceNavigation: (message: string) => void;
  announceStatus: (message: string) => void;
  announceError: (message: string) => void;
  announceSuccess: (message: string) => void;
  clearAnnouncements: () => void;
  isEnabled: boolean;
  setEnabled: (enabled: boolean) => void;
  showVisualFeedback: boolean;
  setShowVisualFeedback: (show: boolean) => void;
  verbosity: 'minimal' | 'normal' | 'verbose';
  setVerbosity: (level: 'minimal' | 'normal' | 'verbose') => void;
}

const ScreenReaderContext = createContext<ScreenReaderContextType | undefined>(undefined);

export function useScreenReader() {
  const context = useContext(ScreenReaderContext);
  if (!context) {
    throw new Error('useScreenReader must be used within a ScreenReaderProvider');
  }
  return context;
}

interface ScreenReaderProviderProps {
  children: React.ReactNode;
}

export function ScreenReaderProvider({ children }: ScreenReaderProviderProps) {
  const [announcements, setAnnouncements] = useState<Announcement[]>([]);
  const [isEnabled, setEnabled] = useState(true);
  const [showVisualFeedback, setShowVisualFeedback] = useState(true);
  const [verbosity, setVerbosity] = useState<'minimal' | 'normal' | 'verbose'>('normal');
  
  const politeRef = useRef<HTMLDivElement>(null);
  const assertiveRef = useRef<HTMLDivElement>(null);
  const statusRef = useRef<HTMLDivElement>(null);

  const announce = useCallback((
    message: string, 
    type: AnnouncementType = 'info', 
    priority: AnnouncementPriority = 'polite',
    persistent: boolean = false
  ) => {
    if (!isEnabled || !message.trim()) return;

    // Apply verbosity filtering
    if (verbosity === 'minimal' && !['error', 'success'].includes(type)) {
      return;
    }

    const announcement: Announcement = {
      id: Date.now().toString() + Math.random(),
      message: message.trim(),
      type,
      priority,
      timestamp: new Date(),
      persistent
    };

    // Add to announcements history
    setAnnouncements(prev => [announcement, ...prev.slice(0, 49)]); // Keep last 50

    // Announce to screen readers
    const targetRef = priority === 'assertive' ? assertiveRef : 
                     type === 'status' ? statusRef : politeRef;
    
    if (targetRef.current) {
      // Clear and set the message
      targetRef.current.textContent = '';
      setTimeout(() => {
        if (targetRef.current) {
          targetRef.current.textContent = formatMessageForScreenReader(message, type);
        }
      }, 100);
    }

    // Auto-clear non-persistent announcements
    if (!persistent) {
      setTimeout(() => {
        setAnnouncements(prev => prev.filter(a => a.id !== announcement.id));
      }, type === 'error' ? 10000 : 5000);
    }
  }, [isEnabled, verbosity]);

  const announceNavigation = useCallback((message: string) => {
    announce(`Navigation: ${message}`, 'navigation', 'polite');
  }, [announce]);

  const announceStatus = useCallback((message: string) => {
    announce(message, 'status', 'polite');
  }, [announce]);

  const announceError = useCallback((message: string) => {
    announce(`Error: ${message}`, 'error', 'assertive', true);
  }, [announce]);

  const announceSuccess = useCallback((message: string) => {
    announce(`Success: ${message}`, 'success', 'polite');
  }, [announce]);

  const clearAnnouncements = useCallback(() => {
    setAnnouncements([]);
    if (politeRef.current) politeRef.current.textContent = '';
    if (assertiveRef.current) assertiveRef.current.textContent = '';
    if (statusRef.current) statusRef.current.textContent = '';
  }, []);

  const formatMessageForScreenReader = (message: string, type: AnnouncementType): string => {
    const prefix = {
      info: '',
      success: 'Success: ',
      warning: 'Warning: ',
      error: 'Error: ',
      navigation: 'Navigated to: ',
      status: 'Status: '
    }[type];

    return `${prefix}${message}`;
  };

  return (
    <ScreenReaderContext.Provider 
      value={{
        announce,
        announceNavigation,
        announceStatus,
        announceError,
        announceSuccess,
        clearAnnouncements,
        isEnabled,
        setEnabled,
        showVisualFeedback,
        setShowVisualFeedback,
        verbosity,
        setVerbosity
      }}
    >
      {children}
      
      {/* Screen Reader Live Regions */}
      <div className="sr-only">
        <div
          ref={politeRef}
          aria-live="polite"
          aria-atomic="true"
          role="status"
        />
        <div
          ref={assertiveRef}
          aria-live="assertive"
          aria-atomic="true"
          role="alert"
        />
        <div
          ref={statusRef}
          aria-live="polite"
          aria-atomic="false"
          role="log"
        />
      </div>

      {/* Visual Feedback */}
      {showVisualFeedback && (
        <VisualAnnouncementFeed announcements={announcements} />
      )}
    </ScreenReaderContext.Provider>
  );
}

interface VisualAnnouncementFeedProps {
  announcements: Announcement[];
}

function VisualAnnouncementFeed({ announcements }: VisualAnnouncementFeedProps) {
  const recentAnnouncements = announcements.slice(0, 3);

  const getIcon = (type: AnnouncementType) => {
    switch (type) {
      case 'success':
        return <CheckCircle className="w-4 h-4 text-green-600" />;
      case 'error':
        return <XCircle className="w-4 h-4 text-red-600" />;
      case 'warning':
        return <AlertTriangle className="w-4 h-4 text-yellow-600" />;
      case 'navigation':
        return <MessageSquare className="w-4 h-4 text-blue-600" />;
      case 'status':
        return <Bell className="w-4 h-4 text-purple-600" />;
      default:
        return <Info className="w-4 h-4 text-gray-600" />;
    }
  };

  const getBackgroundColor = (type: AnnouncementType) => {
    switch (type) {
      case 'success':
        return 'bg-green-50 border-green-200 text-green-800';
      case 'error':
        return 'bg-red-50 border-red-200 text-red-800';
      case 'warning':
        return 'bg-yellow-50 border-yellow-200 text-yellow-800';
      case 'navigation':
        return 'bg-blue-50 border-blue-200 text-blue-800';
      case 'status':
        return 'bg-purple-50 border-purple-200 text-purple-800';
      default:
        return 'bg-gray-50 border-gray-200 text-gray-800';
    }
  };

  if (recentAnnouncements.length === 0) return null;

  return (
    <div className="fixed top-4 right-4 z-50 space-y-2 max-w-sm">
      <AnimatePresence>
        {recentAnnouncements.map((announcement) => (
          <motion.div
            key={announcement.id}
            initial={{ opacity: 0, x: 300, scale: 0.8 }}
            animate={{ opacity: 1, x: 0, scale: 1 }}
            exit={{ opacity: 0, x: 300, scale: 0.8 }}
            transition={{ duration: 0.3 }}
            className={`
              p-3 rounded-lg border shadow-lg
              ${getBackgroundColor(announcement.type)}
            `}
            role="status"
            aria-live="polite"
          >
            <div className="flex items-start space-x-2">
              {getIcon(announcement.type)}
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium">
                  {announcement.message}
                </p>
                <p className="text-xs opacity-75 mt-1">
                  {announcement.timestamp.toLocaleTimeString()}
                </p>
              </div>
            </div>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}

interface ScreenReaderControlsProps {
  className?: string;
}

export function ScreenReaderControls({ className = '' }: ScreenReaderControlsProps) {
  const {
    isEnabled,
    setEnabled,
    showVisualFeedback,
    setShowVisualFeedback,
    verbosity,
    setVerbosity,
    clearAnnouncements,
    announcements
  } = useScreenReader();

  const [showSettings, setShowSettings] = useState(false);

  return (
    <div className={`relative ${className}`}>
      <motion.button
        onClick={() => setShowSettings(!showSettings)}
        className={`
          p-3 rounded-lg border-2 transition-all
          ${isEnabled 
            ? 'bg-blue-500 border-blue-500 text-white shadow-lg' 
            : 'bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-400'
          }
          hover:scale-105 focus:ring-2 focus:ring-blue-500
        `}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        aria-label={`Screen reader announcements ${isEnabled ? 'enabled' : 'disabled'}`}
        aria-expanded={showSettings}
        aria-haspopup="menu"
      >
        {isEnabled ? <Volume2 size={20} /> : <VolumeX size={20} />}
      </motion.button>

      {/* Settings Panel */}
      <AnimatePresence>
        {showSettings && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: -10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: -10 }}
            className="absolute top-full mt-2 right-0 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg p-4 min-w-64 z-50"
            role="menu"
            aria-label="Screen reader settings"
          >
            <h4 className="font-semibold text-gray-900 dark:text-white mb-3">
              Screen Reader Settings
            </h4>

            <div className="space-y-4">
              {/* Enable/Disable */}
              <label className="flex items-center space-x-3">
                <input
                  type="checkbox"
                  checked={isEnabled}
                  onChange={(e) => setEnabled(e.target.checked)}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700 dark:text-gray-300">
                  Enable announcements
                </span>
              </label>

              {/* Visual Feedback */}
              <label className="flex items-center space-x-3">
                <input
                  type="checkbox"
                  checked={showVisualFeedback}
                  onChange={(e) => setShowVisualFeedback(e.target.checked)}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700 dark:text-gray-300">
                  Show visual feedback
                </span>
              </label>

              {/* Verbosity Level */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Announcement Level
                </label>
                <select
                  value={verbosity}
                  onChange={(e) => setVerbosity(e.target.value as any)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
                >
                  <option value="minimal">Minimal (Errors & Success only)</option>
                  <option value="normal">Normal (Standard announcements)</option>
                  <option value="verbose">Verbose (All announcements)</option>
                </select>
              </div>

              {/* Clear Button */}
              <button
                onClick={clearAnnouncements}
                className="w-full px-3 py-2 text-sm bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-md transition-colors"
              >
                Clear All Announcements
              </button>
            </div>

            {/* Status */}
            <div className="mt-4 pt-3 border-t border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                <span>Status:</span>
                <span className={isEnabled ? 'text-green-600' : 'text-red-600'}>
                  {isEnabled ? 'Active' : 'Disabled'}
                </span>
              </div>
              <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
                <span>Recent announcements:</span>
                <span>{announcements?.length || 0}</span>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Click outside to close */}
      {showSettings && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setShowSettings(false)}
          aria-hidden="true"
        />
      )}
    </div>
  );
}

// Hook for components to easily announce changes
export function useAnnouncement() {
  const { announce, announceNavigation, announceStatus, announceError, announceSuccess } = useScreenReader();

  return {
    announce,
    announceNavigation,
    announceStatus, 
    announceError,
    announceSuccess
  };
}

// Utility component for page announcements
interface PageAnnouncementProps {
  title: string;
  description?: string;
  children?: React.ReactNode;
}

export function PageAnnouncement({ title, description, children }: PageAnnouncementProps) {
  const { announceNavigation } = useScreenReader();

  React.useEffect(() => {
    const announcement = description ? `${title}. ${description}` : title;
    announceNavigation(announcement);
  }, [title, description, announceNavigation]);

  return (
    <div className="sr-only" aria-live="polite" role="main">
      <h1>{title}</h1>
      {description && <p>{description}</p>}
      {children}
    </div>
  );
}

// CSS to be added to globals.css
export const screenReaderStyles = `
/* Screen Reader Only Content */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

/* Make screen reader only content visible when focused */
.sr-only:focus,
.sr-only:active {
  position: static;
  width: auto;
  height: auto;
  padding: inherit;
  margin: inherit;
  overflow: visible;
  clip: auto;
  white-space: normal;
}

/* Live regions should not be hidden */
[aria-live],
[role="status"],
[role="alert"],
[role="log"] {
  position: absolute !important;
  left: -10000px !important;
  width: 1px !important;
  height: 1px !important;
  overflow: hidden !important;
}
`;
