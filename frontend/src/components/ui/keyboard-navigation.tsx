'use client';

import React, { useState, useEffect, useRef, createContext, useContext } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Keyboard, ArrowUp, ArrowDown, ArrowLeft, ArrowRight, Enter, Escape } from 'lucide-react';

interface FocusableElement {
  id: string;
  element: HTMLElement;
  tabIndex: number;
  role?: string;
  label?: string;
  group?: string;
}

interface KeyboardNavigationContextType {
  focusedId: string | null;
  setFocusedId: (id: string | null) => void;
  registerElement: (element: FocusableElement) => void;
  unregisterElement: (id: string) => void;
  isKeyboardNavigation: boolean;
  setKeyboardNavigation: (enabled: boolean) => void;
  showFocusIndicators: boolean;
  setShowFocusIndicators: (show: boolean) => void;
}

const KeyboardNavigationContext = createContext<KeyboardNavigationContextType | undefined>(undefined);

export function useKeyboardNavigation() {
  const context = useContext(KeyboardNavigationContext);
  if (!context) {
    throw new Error('useKeyboardNavigation must be used within a KeyboardNavigationProvider');
  }
  return context;
}

interface KeyboardNavigationProviderProps {
  children: React.ReactNode;
}

export function KeyboardNavigationProvider({ children }: KeyboardNavigationProviderProps) {
  const [focusedId, setFocusedId] = useState<string | null>(null);
  const [elements, setElements] = useState<Map<string, FocusableElement>>(new Map());
  const [isKeyboardNavigation, setKeyboardNavigation] = useState(true);
  const [showFocusIndicators, setShowFocusIndicators] = useState(false);
  const [lastInteractionWasKeyboard, setLastInteractionWasKeyboard] = useState(false);

  const elementOrder = useRef<string[]>([]);

  const registerElement = (element: FocusableElement) => {
    setElements(prev => {
      const newMap = new Map(prev);
      newMap.set(element.id, element);
      
      // Update element order based on DOM position and tabIndex
      elementOrder.current = Array.from(newMap.values())
        .sort((a, b) => {
          // First sort by tabIndex
          if (a.tabIndex !== b.tabIndex) {
            if (a.tabIndex === -1) return 1;
            if (b.tabIndex === -1) return -1;
            return a.tabIndex - b.tabIndex;
          }
          
          // Then by DOM position
          const position = a.element.compareDocumentPosition(b.element);
          if (position & Node.DOCUMENT_POSITION_FOLLOWING) return -1;
          if (position & Node.DOCUMENT_POSITION_PRECEDING) return 1;
          return 0;
        })
        .map(el => el.id);
      
      return newMap;
    });
  };

  const unregisterElement = (id: string) => {
    setElements(prev => {
      const newMap = new Map(prev);
      newMap.delete(id);
      elementOrder.current = elementOrder.current.filter(elId => elId !== id);
      return newMap;
    });
  };

  // Keyboard event handler
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isKeyboardNavigation) return;

      setLastInteractionWasKeyboard(true);
      setShowFocusIndicators(true);

      const currentIndex = focusedId ? elementOrder.current.indexOf(focusedId) : -1;
      let nextIndex = currentIndex;

      switch (e.key) {
        case 'Tab':
          e.preventDefault();
          if (e.shiftKey) {
            nextIndex = currentIndex <= 0 ? elementOrder.current.length - 1 : currentIndex - 1;
          } else {
            nextIndex = currentIndex >= elementOrder.current.length - 1 ? 0 : currentIndex + 1;
          }
          break;

        case 'ArrowDown':
          e.preventDefault();
          nextIndex = currentIndex >= elementOrder.current.length - 1 ? 0 : currentIndex + 1;
          break;

        case 'ArrowUp':
          e.preventDefault();
          nextIndex = currentIndex <= 0 ? elementOrder.current.length - 1 : currentIndex - 1;
          break;

        case 'ArrowRight':
          // Handle horizontal navigation within groups
          if (focusedId) {
            const currentElement = elements.get(focusedId);
            if (currentElement?.group) {
              const groupElements = elementOrder.current.filter(id => {
                const el = elements.get(id);
                return el?.group === currentElement.group;
              });
              const groupIndex = groupElements.indexOf(focusedId);
              if (groupIndex < groupElements.length - 1) {
                e.preventDefault();
                const nextId = groupElements[groupIndex + 1];
                nextIndex = elementOrder.current.indexOf(nextId);
              }
            }
          }
          break;

        case 'ArrowLeft':
          // Handle horizontal navigation within groups
          if (focusedId) {
            const currentElement = elements.get(focusedId);
            if (currentElement?.group) {
              const groupElements = elementOrder.current.filter(id => {
                const el = elements.get(id);
                return el?.group === currentElement.group;
              });
              const groupIndex = groupElements.indexOf(focusedId);
              if (groupIndex > 0) {
                e.preventDefault();
                const prevId = groupElements[groupIndex - 1];
                nextIndex = elementOrder.current.indexOf(prevId);
              }
            }
          }
          break;

        case 'Enter':
        case ' ':
          if (focusedId) {
            const element = elements.get(focusedId)?.element;
            if (element) {
              e.preventDefault();
              element.click();
            }
          }
          break;

        case 'Escape':
          e.preventDefault();
          setFocusedId(null);
          break;

        case 'Home':
          e.preventDefault();
          nextIndex = 0;
          break;

        case 'End':
          e.preventDefault();
          nextIndex = elementOrder.current.length - 1;
          break;

        default:
          return;
      }

      if (nextIndex !== currentIndex && nextIndex >= 0 && nextIndex < elementOrder.current.length) {
        const nextId = elementOrder.current[nextIndex];
        setFocusedId(nextId);
        const nextElement = elements.get(nextId)?.element;
        if (nextElement) {
          nextElement.focus();
        }
      }
    };

    const handleMouseDown = () => {
      setLastInteractionWasKeyboard(false);
      // Hide focus indicators after a short delay if interaction was mouse-based
      setTimeout(() => {
        if (!lastInteractionWasKeyboard) {
          setShowFocusIndicators(false);
        }
      }, 100);
    };

    const handleFocusIn = (e: FocusEvent) => {
      const target = e.target as HTMLElement;
      const elementId = Array.from(elements.entries()).find(([, el]) => el.element === target)?.[0];
      if (elementId) {
        setFocusedId(elementId);
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    document.addEventListener('mousedown', handleMouseDown);
    document.addEventListener('focusin', handleFocusIn);

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('mousedown', handleMouseDown);
      document.removeEventListener('focusin', handleFocusIn);
    };
  }, [focusedId, elements, isKeyboardNavigation, lastInteractionWasKeyboard]);

  return (
    <KeyboardNavigationContext.Provider 
      value={{
        focusedId,
        setFocusedId,
        registerElement,
        unregisterElement,
        isKeyboardNavigation,
        setKeyboardNavigation,
        showFocusIndicators,
        setShowFocusIndicators
      }}
    >
      {children}
    </KeyboardNavigationContext.Provider>
  );
}

interface KeyboardNavigableProps {
  id: string;
  children: React.ReactNode;
  tabIndex?: number;
  role?: string;
  label?: string;
  group?: string;
  onFocus?: () => void;
  onBlur?: () => void;
  className?: string;
  disabled?: boolean;
}

export function KeyboardNavigable({
  id,
  children,
  tabIndex = 0,
  role,
  label,
  group,
  onFocus,
  onBlur,
  className = '',
  disabled = false
}: KeyboardNavigableProps) {
  const ref = useRef<HTMLDivElement>(null);
  const { 
    focusedId, 
    registerElement, 
    unregisterElement, 
    showFocusIndicators 
  } = useKeyboardNavigation();
  
  const isFocused = focusedId === id;

  useEffect(() => {
    const element = ref.current;
    if (element && !disabled) {
      registerElement({
        id,
        element,
        tabIndex,
        role,
        label,
        group
      });

      return () => unregisterElement(id);
    }
  }, [id, tabIndex, role, label, group, disabled, registerElement, unregisterElement]);

  const handleFocus = () => {
    onFocus?.();
  };

  const handleBlur = () => {
    onBlur?.();
  };

  return (
    <div
      ref={ref}
      tabIndex={disabled ? -1 : tabIndex}
      role={role}
      aria-label={label}
      onFocus={handleFocus}
      onBlur={handleBlur}
      className={`
        relative outline-none
        ${isFocused && showFocusIndicators ? 'keyboard-focused' : ''}
        ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
        ${className}
      `}
    >
      {children}
      
      {/* Focus indicator */}
      <AnimatePresence>
        {isFocused && showFocusIndicators && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="absolute inset-0 border-2 border-blue-500 rounded-lg pointer-events-none"
            style={{ zIndex: 1000 }}
          />
        )}
      </AnimatePresence>
    </div>
  );
}

interface KeyboardNavigationIndicatorProps {
  position?: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right';
  className?: string;
}

export function KeyboardNavigationIndicator({ 
  position = 'bottom-right',
  className = '' 
}: KeyboardNavigationIndicatorProps) {
  const { 
    isKeyboardNavigation, 
    setKeyboardNavigation,
    showFocusIndicators,
    focusedId
  } = useKeyboardNavigation();
  
  const [showHelp, setShowHelp] = useState(false);

  const positionClasses = {
    'top-left': 'top-4 left-4',
    'top-right': 'top-4 right-4',
    'bottom-left': 'bottom-4 left-4',
    'bottom-right': 'bottom-4 right-4'
  };

  const keyboardShortcuts = [
    { key: 'Tab', description: 'Navigate forward' },
    { key: 'Shift + Tab', description: 'Navigate backward' },
    { key: '↓ ↑', description: 'Navigate vertically' },
    { key: '← →', description: 'Navigate within groups' },
    { key: 'Enter/Space', description: 'Activate element' },
    { key: 'Escape', description: 'Clear focus' },
    { key: 'Home/End', description: 'First/Last element' }
  ];

  return (
    <div className={`fixed ${positionClasses[position]} z-50 ${className}`}>
      <div className="flex items-center space-x-2">
        {/* Keyboard navigation toggle */}
        <motion.button
          onClick={() => setKeyboardNavigation(!isKeyboardNavigation)}
          className={`
            p-3 rounded-lg border-2 transition-all
            ${isKeyboardNavigation 
              ? 'bg-blue-500 border-blue-500 text-white shadow-lg' 
              : 'bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-400'
            }
            hover:scale-105 focus:ring-2 focus:ring-blue-500
          `}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          aria-label={`${isKeyboardNavigation ? 'Disable' : 'Enable'} keyboard navigation`}
          title={`${isKeyboardNavigation ? 'Disable' : 'Enable'} keyboard navigation`}
        >
          <Keyboard size={20} />
        </motion.button>

        {/* Help button */}
        <motion.button
          onClick={() => setShowHelp(!showHelp)}
          className="p-3 bg-white dark:bg-gray-800 border-2 border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 rounded-lg hover:scale-105 focus:ring-2 focus:ring-blue-500"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          aria-label="Show keyboard shortcuts help"
          title="Show keyboard shortcuts"
        >
          ?
        </motion.button>
      </div>

      {/* Status indicator */}
      {isKeyboardNavigation && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-2 text-xs text-center"
        >
          <div className={`
            px-2 py-1 rounded-full text-xs
            ${showFocusIndicators 
              ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' 
              : 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400'
            }
          `}>
            {showFocusIndicators ? 'Keyboard Active' : 'Mouse Mode'}
          </div>
          {focusedId && (
            <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Focused: {focusedId}
            </div>
          )}
        </motion.div>
      )}

      {/* Help overlay */}
      <AnimatePresence>
        {showHelp && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 10 }}
            className="absolute bottom-full mb-2 right-0 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg p-4 min-w-64"
          >
            <h4 className="font-semibold text-gray-900 dark:text-white mb-3">
              Keyboard Shortcuts
            </h4>
            <div className="space-y-2">
              {keyboardShortcuts.map((shortcut, index) => (
                <div key={index} className="flex items-center justify-between text-sm">
                  <span className="text-gray-600 dark:text-gray-400">
                    {shortcut.description}
                  </span>
                  <kbd className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded text-xs font-mono">
                    {shortcut.key}
                  </kbd>
                </div>
              ))}
            </div>
            
            <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
              <div className="flex items-center space-x-2 text-xs text-gray-500 dark:text-gray-400">
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                <span>Focus indicators show navigation path</span>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Click outside to close help */}
      {showHelp && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setShowHelp(false)}
          aria-hidden="true"
        />
      )}
    </div>
  );
}

// CSS to be added to globals.css for keyboard navigation
export const keyboardNavigationStyles = `
/* Keyboard Navigation Styles */
.keyboard-focused {
  position: relative;
}

.keyboard-focused::after {
  content: '';
  position: absolute;
  inset: -2px;
  border: 2px solid #3b82f6;
  border-radius: 6px;
  pointer-events: none;
  z-index: 1000;
  animation: focusGlow 0.3s ease-out;
}

@keyframes focusGlow {
  0% {
    opacity: 0;
    transform: scale(0.95);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}

/* High contrast mode keyboard focus */
[data-high-contrast="true"] .keyboard-focused::after {
  border-color: var(--high-contrast-focus);
  border-width: 3px;
  box-shadow: 0 0 0 1px var(--high-contrast-bg);
}

/* Skip to content link */
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

/* Ensure interactive elements are focusable */
button:focus-visible,
a:focus-visible,
input:focus-visible,
select:focus-visible,
textarea:focus-visible,
[tabindex]:focus-visible {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
  border-radius: 4px;
}

/* Remove default focus styles in favor of our custom ones */
button:focus,
a:focus,
input:focus,
select:focus,
textarea:focus,
[tabindex]:focus {
  outline: none;
}
`;
