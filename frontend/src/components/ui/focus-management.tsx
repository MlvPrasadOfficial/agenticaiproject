'use client';

import React, { createContext, useContext, useRef, useCallback, useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Target, ArrowLeft, RotateCcw, Settings } from 'lucide-react';

interface FocusHistoryEntry {
  element: HTMLElement;
  timestamp: Date;
  reason: string;
}

interface FocusContextType {
  focusElement: (element: HTMLElement | string, reason?: string) => void;
  focusFirst: (container?: HTMLElement | string) => void;
  focusLast: (container?: HTMLElement | string) => void;
  returnFocus: () => void;
  trapFocus: (container: HTMLElement | string) => () => void;
  setFocusTrap: (active: boolean, container?: HTMLElement | string) => void;
  getFocusableElements: (container?: HTMLElement) => HTMLElement[];
  focusHistory: FocusHistoryEntry[];
  clearHistory: () => void;
  restorePreviousFocus: () => void;
  enableFocusVisible: boolean;
  setEnableFocusVisible: (enabled: boolean) => void;
}

const FocusContext = createContext<FocusContextType | undefined>(undefined);

export function useFocusManager() {
  const context = useContext(FocusContext);
  if (!context) {
    throw new Error('useFocusManager must be used within a FocusManagerProvider');
  }
  return context;
}

interface FocusManagerProviderProps {
  children: React.ReactNode;
}

export function FocusManagerProvider({ children }: FocusManagerProviderProps) {
  const [focusHistory, setFocusHistory] = useState<FocusHistoryEntry[]>([]);
  const [activeTrapContainer, setActiveTrapContainer] = useState<HTMLElement | null>(null);
  const [enableFocusVisible, setEnableFocusVisible] = useState(true);
  
  const lastFocusedElement = useRef<HTMLElement | null>(null);
  const trapCleanupRef = useRef<(() => void) | null>(null);

  // Selectors for focusable elements
  const focusableSelectors = [
    'a[href]',
    'button:not([disabled])',
    'input:not([disabled])',
    'select:not([disabled])',
    'textarea:not([disabled])',
    '[tabindex]:not([tabindex="-1"])',
    '[contenteditable="true"]',
    'details > summary',
    'audio[controls]',
    'video[controls]'
  ].join(', ');

  const getFocusableElements = useCallback((container: HTMLElement = document.body): HTMLElement[] => {
    const elements = Array.from(container.querySelectorAll(focusableSelectors)) as HTMLElement[];
    return elements.filter(element => {
      return (
        element.offsetWidth > 0 ||
        element.offsetHeight > 0 ||
        element.getClientRects().length > 0
      ) && !element.hasAttribute('disabled');
    });
  }, []);

  const resolveElement = useCallback((elementOrSelector: HTMLElement | string): HTMLElement | null => {
    if (typeof elementOrSelector === 'string') {
      return document.querySelector(elementOrSelector);
    }
    return elementOrSelector;
  }, []);

  const addToHistory = useCallback((element: HTMLElement, reason: string) => {
    setFocusHistory(prev => [
      { element, timestamp: new Date(), reason },
      ...prev.slice(0, 19) // Keep last 20 entries
    ]);
  }, []);

  const focusElement = useCallback((elementOrSelector: HTMLElement | string, reason = 'programmatic') => {
    const element = resolveElement(elementOrSelector);
    if (!element) return;

    // Store current focus for history
    if (document.activeElement && document.activeElement !== element) {
      lastFocusedElement.current = document.activeElement as HTMLElement;
      addToHistory(lastFocusedElement.current, `before focusing ${reason}`);
    }

    element.focus();
    addToHistory(element, reason);
  }, [resolveElement, addToHistory]);

  const focusFirst = useCallback((containerOrSelector?: HTMLElement | string) => {
    const container = containerOrSelector ? resolveElement(containerOrSelector) : document.body;
    if (!container) return;

    const focusableElements = getFocusableElements(container);
    if (focusableElements.length > 0) {
      focusElement(focusableElements[0], 'focus first');
    }
  }, [resolveElement, getFocusableElements, focusElement]);

  const focusLast = useCallback((containerOrSelector?: HTMLElement | string) => {
    const container = containerOrSelector ? resolveElement(containerOrSelector) : document.body;
    if (!container) return;

    const focusableElements = getFocusableElements(container);
    if (focusableElements.length > 0) {
      focusElement(focusableElements[focusableElements.length - 1], 'focus last');
    }
  }, [resolveElement, getFocusableElements, focusElement]);

  const returnFocus = useCallback(() => {
    if (lastFocusedElement.current) {
      focusElement(lastFocusedElement.current, 'return focus');
    }
  }, [focusElement]);

  const restorePreviousFocus = useCallback(() => {
    if (focusHistory.length > 1) {
      const previousEntry = focusHistory[1];
      if (previousEntry && previousEntry.element) {
        focusElement(previousEntry.element, 'restore previous focus');
      }
    }
  }, [focusHistory, focusElement]);

  const trapFocus = useCallback((containerOrSelector: HTMLElement | string) => {
    const container = resolveElement(containerOrSelector);
    if (!container) return () => {};

    const focusableElements = getFocusableElements(container);
    if (focusableElements.length === 0) return () => {};

    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    // Focus the first element initially
    firstElement.focus();

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return;

      if (e.shiftKey) {
        // Shift + Tab
        if (document.activeElement === firstElement) {
          e.preventDefault();
          lastElement.focus();
        }
      } else {
        // Tab
        if (document.activeElement === lastElement) {
          e.preventDefault();
          firstElement.focus();
        }
      }
    };

    const handleFocusOut = (e: FocusEvent) => {
      // If focus moves outside the container, bring it back
      if (!container.contains(e.relatedTarget as Node)) {
        firstElement.focus();
      }
    };

    container.addEventListener('keydown', handleKeyDown);
    container.addEventListener('focusout', handleFocusOut);

    return () => {
      container.removeEventListener('keydown', handleKeyDown);
      container.removeEventListener('focusout', handleFocusOut);
    };
  }, [resolveElement, getFocusableElements]);

  const setFocusTrap = useCallback((active: boolean, containerOrSelector?: HTMLElement | string) => {
    // Clean up existing trap
    if (trapCleanupRef.current) {
      trapCleanupRef.current();
      trapCleanupRef.current = null;
      setActiveTrapContainer(null);
    }

    if (active && containerOrSelector) {
      const container = resolveElement(containerOrSelector);
      if (container) {
        trapCleanupRef.current = trapFocus(container);
        setActiveTrapContainer(container);
      }
    }
  }, [resolveElement, trapFocus]);

  const clearHistory = useCallback(() => {
    setFocusHistory([]);
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (trapCleanupRef.current) {
        trapCleanupRef.current();
      }
    };
  }, []);

  // Add focus-visible support
  useEffect(() => {
    if (!enableFocusVisible) return;

    let hadKeyboardEvent = false;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.metaKey || e.altKey || e.ctrlKey) return;
      hadKeyboardEvent = true;
    };

    const handlePointerDown = () => {
      hadKeyboardEvent = false;
    };

    const handleFocus = (e: FocusEvent) => {
      const target = e.target as HTMLElement;
      if (hadKeyboardEvent || target.matches(':focus-visible')) {
        target.setAttribute('data-focus-visible', '');
      }
    };

    const handleBlur = (e: FocusEvent) => {
      const target = e.target as HTMLElement;
      target.removeAttribute('data-focus-visible');
    };

    document.addEventListener('keydown', handleKeyDown, true);
    document.addEventListener('pointerdown', handlePointerDown, true);
    document.addEventListener('focus', handleFocus, true);
    document.addEventListener('blur', handleBlur, true);

    return () => {
      document.removeEventListener('keydown', handleKeyDown, true);
      document.removeEventListener('pointerdown', handlePointerDown, true);
      document.removeEventListener('focus', handleFocus, true);
      document.removeEventListener('blur', handleBlur, true);
    };
  }, [enableFocusVisible]);

  return (
    <FocusContext.Provider 
      value={{
        focusElement,
        focusFirst,
        focusLast,
        returnFocus,
        trapFocus,
        setFocusTrap,
        getFocusableElements,
        focusHistory,
        clearHistory,
        restorePreviousFocus,
        enableFocusVisible,
        setEnableFocusVisible
      }}
    >
      {children}
    </FocusContext.Provider>
  );
}

interface FocusTrapProps {
  active: boolean;
  children: React.ReactNode;
  restoreFocus?: boolean;
  className?: string;
}

export function FocusTrap({ active, children, restoreFocus = true, className = '' }: FocusTrapProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const { setFocusTrap, returnFocus } = useFocusManager();
  const previousFocus = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (active) {
      previousFocus.current = document.activeElement as HTMLElement;
      if (containerRef.current) {
        setFocusTrap(true, containerRef.current);
      }
    } else {
      setFocusTrap(false);
      if (restoreFocus && previousFocus.current) {
        previousFocus.current.focus();
      }
    }

    return () => {
      setFocusTrap(false);
    };
  }, [active, setFocusTrap, restoreFocus]);

  return (
    <div ref={containerRef} className={className}>
      {children}
    </div>
  );
}

interface FocusManagerControlsProps {
  showHistory?: boolean;
  className?: string;
}

export function FocusManagerControls({ showHistory = true, className = '' }: FocusManagerControlsProps) {
  const {
    focusHistory,
    clearHistory,
    restorePreviousFocus,
    returnFocus,
    enableFocusVisible,
    setEnableFocusVisible
  } = useFocusManager();

  const [showSettings, setShowSettings] = useState(false);

  const formatTimestamp = (date: Date) => {
    return date.toLocaleTimeString();
  };

  return (
    <div className={`relative ${className}`}>
      <motion.button
        onClick={() => setShowSettings(!showSettings)}
        className="p-3 bg-white dark:bg-gray-800 border-2 border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 rounded-lg hover:scale-105 focus:ring-2 focus:ring-blue-500"
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        aria-label="Focus management controls"
        aria-expanded={showSettings}
      >
        <Target size={20} />
      </motion.button>

      <AnimatePresence>
        {showSettings && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: -10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: -10 }}
            className="absolute top-full mt-2 right-0 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg p-4 min-w-80 max-w-md z-50"
            role="menu"
            aria-label="Focus management settings"
          >
            <h4 className="font-semibold text-gray-900 dark:text-white mb-3">
              Focus Management
            </h4>

            {/* Controls */}
            <div className="space-y-3 mb-4">
              <div className="flex space-x-2">
                <button
                  onClick={returnFocus}
                  className="flex-1 px-3 py-2 text-sm bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 hover:bg-blue-200 dark:hover:bg-blue-900/30 rounded-md transition-colors flex items-center justify-center space-x-1"
                >
                  <ArrowLeft size={14} />
                  <span>Return</span>
                </button>
                
                <button
                  onClick={restorePreviousFocus}
                  className="flex-1 px-3 py-2 text-sm bg-purple-100 dark:bg-purple-900/20 text-purple-700 dark:text-purple-300 hover:bg-purple-200 dark:hover:bg-purple-900/30 rounded-md transition-colors flex items-center justify-center space-x-1"
                >
                  <RotateCcw size={14} />
                  <span>Previous</span>
                </button>
                
                <button
                  onClick={clearHistory}
                  className="flex-1 px-3 py-2 text-sm bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-md transition-colors"
                >
                  Clear
                </button>
              </div>

              {/* Settings */}
              <label className="flex items-center space-x-3">
                <input
                  type="checkbox"
                  checked={enableFocusVisible}
                  onChange={(e) => setEnableFocusVisible(e.target.checked)}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700 dark:text-gray-300">
                  Enable focus-visible indicators
                </span>
              </label>
            </div>

            {/* Focus History */}
            {showHistory && (
              <div>
                <div className="flex items-center justify-between mb-2">
                  <h5 className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Focus History
                  </h5>
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    {focusHistory.length} entries
                  </span>
                </div>
                
                <div className="max-h-48 overflow-y-auto space-y-1">
                  {focusHistory.length === 0 ? (
                    <p className="text-xs text-gray-500 dark:text-gray-400 italic">
                      No focus history yet
                    </p>
                  ) : (
                    focusHistory.slice(0, 10).map((entry, index) => (
                      <div
                        key={index}
                        className="p-2 bg-gray-50 dark:bg-gray-700/50 rounded text-xs"
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-mono text-gray-600 dark:text-gray-400">
                            {entry.element.tagName.toLowerCase()}
                            {entry.element.id && `#${entry.element.id}`}
                            {entry.element.className && `.${entry.element.className.split(' ')[0]}`}
                          </span>
                          <span className="text-gray-500 dark:text-gray-400">
                            {formatTimestamp(entry.timestamp)}
                          </span>
                        </div>
                        <div className="text-gray-600 dark:text-gray-400 mt-1">
                          {entry.reason}
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            )}

            {/* Stats */}
            <div className="mt-4 pt-3 border-t border-gray-200 dark:border-gray-700">
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="text-center p-2 bg-gray-50 dark:bg-gray-700/50 rounded">
                  <div className="font-semibold text-gray-900 dark:text-white">
                    {focusHistory.length}
                  </div>
                  <div className="text-gray-500 dark:text-gray-400">
                    Total Focuses
                  </div>
                </div>
                <div className="text-center p-2 bg-gray-50 dark:bg-gray-700/50 rounded">
                  <div className="font-semibold text-gray-900 dark:text-white">
                    {document.activeElement?.tagName.toLowerCase() || 'none'}
                  </div>
                  <div className="text-gray-500 dark:text-gray-400">
                    Current Focus
                  </div>
                </div>
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

// Utility hook for modal focus management
export function useModalFocus(isOpen: boolean, initialFocusRef?: React.RefObject<HTMLElement>) {
  const { setFocusTrap } = useFocusManager();
  const modalRef = useRef<HTMLDivElement>(null);
  const previousFocus = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (isOpen) {
      previousFocus.current = document.activeElement as HTMLElement;
      
      if (modalRef.current) {
        setFocusTrap(true, modalRef.current);
        
        // Focus initial element or first focusable element
        if (initialFocusRef?.current) {
          initialFocusRef.current.focus();
        } else {
          const focusableElements = modalRef.current.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
          );
          if (focusableElements.length > 0) {
            (focusableElements[0] as HTMLElement).focus();
          }
        }
      }
    } else {
      setFocusTrap(false);
      // Restore focus when modal closes
      if (previousFocus.current) {
        previousFocus.current.focus();
      }
    }
  }, [isOpen, setFocusTrap, initialFocusRef]);

  return modalRef;
}

// CSS to be added to globals.css
export const focusManagementStyles = `
/* Focus Management Styles */
[data-focus-visible] {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
  border-radius: 4px;
}

/* High contrast focus indicators */
[data-high-contrast="true"] [data-focus-visible] {
  outline: 3px solid var(--high-contrast-focus);
  outline-offset: 2px;
  box-shadow: 0 0 0 1px var(--high-contrast-bg);
}

/* Remove default focus styles when using focus-visible */
*:focus:not([data-focus-visible]) {
  outline: none;
}

/* Focus trap container */
.focus-trap-active {
  isolation: isolate;
}

/* Skip links for focus management */
.skip-link {
  position: absolute;
  top: -40px;
  left: 6px;
  background: #000;
  color: #fff;
  padding: 8px;
  text-decoration: none;
  border-radius: 4px;
  z-index: 9999;
  transition: top 0.3s;
}

.skip-link:focus {
  top: 6px;
}
`;
