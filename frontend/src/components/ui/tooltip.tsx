'use client';

import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { createPortal } from 'react-dom';

interface TooltipProps {
  content: React.ReactNode;
  children: React.ReactNode;
  position?: 'top' | 'bottom' | 'left' | 'right' | 'auto';
  delay?: number;
  offset?: number;
  className?: string;
  maxWidth?: number;
  disabled?: boolean;
  trigger?: 'hover' | 'click' | 'focus';
  arrow?: boolean;
  theme?: 'dark' | 'light' | 'error' | 'warning' | 'success' | 'info';
}

export function Tooltip({
  content,
  children,
  position = 'auto',
  delay = 150,
  offset = 8,
  className = '',
  maxWidth = 200,
  disabled = false,
  trigger = 'hover',
  arrow = true,
  theme = 'dark'
}: TooltipProps) {
  const [isVisible, setIsVisible] = useState(false);
  const [actualPosition, setActualPosition] = useState<'top' | 'bottom' | 'left' | 'right'>('top');
  const [tooltipStyle, setTooltipStyle] = useState<React.CSSProperties>({});
  const triggerRef = useRef<HTMLDivElement>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);
  const timeoutRef = useRef<NodeJS.Timeout>();

  // Calculate optimal position for tooltip
  const calculatePosition = () => {
    if (!triggerRef.current || !tooltipRef.current) return;

    const triggerRect = triggerRef.current.getBoundingClientRect();
    const tooltipRect = tooltipRef.current.getBoundingClientRect();
    const viewport = {
      width: window.innerWidth,
      height: window.innerHeight
    };

    let finalPosition = position;
    let top = 0;
    let left = 0;

    // Auto-positioning logic
    if (position === 'auto') {
      const spaceTop = triggerRect.top;
      const spaceBottom = viewport.height - triggerRect.bottom;
      const spaceLeft = triggerRect.left;
      const spaceRight = viewport.width - triggerRect.right;

      if (spaceTop >= tooltipRect.height + offset) {
        finalPosition = 'top';
      } else if (spaceBottom >= tooltipRect.height + offset) {
        finalPosition = 'bottom';
      } else if (spaceRight >= tooltipRect.width + offset) {
        finalPosition = 'right';
      } else if (spaceLeft >= tooltipRect.width + offset) {
        finalPosition = 'left';
      } else {
        // Default to bottom if no space
        finalPosition = 'bottom';
      }
    }

    // Calculate position based on final position
    switch (finalPosition) {
      case 'top':
        top = triggerRect.top - tooltipRect.height - offset;
        left = triggerRect.left + (triggerRect.width - tooltipRect.width) / 2;
        break;
      case 'bottom':
        top = triggerRect.bottom + offset;
        left = triggerRect.left + (triggerRect.width - tooltipRect.width) / 2;
        break;
      case 'left':
        top = triggerRect.top + (triggerRect.height - tooltipRect.height) / 2;
        left = triggerRect.left - tooltipRect.width - offset;
        break;
      case 'right':
        top = triggerRect.top + (triggerRect.height - tooltipRect.height) / 2;
        left = triggerRect.right + offset;
        break;
    }

    // Ensure tooltip stays within viewport
    if (left < 8) left = 8;
    if (left + tooltipRect.width > viewport.width - 8) {
      left = viewport.width - tooltipRect.width - 8;
    }
    if (top < 8) top = 8;
    if (top + tooltipRect.height > viewport.height - 8) {
      top = viewport.height - tooltipRect.height - 8;
    }

    setActualPosition(finalPosition);
    setTooltipStyle({
      position: 'fixed',
      top: `${top}px`,
      left: `${left}px`,
      zIndex: 9999
    });
  };

  // Show tooltip with delay
  const showTooltip = () => {
    if (disabled) return;
    
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    
    timeoutRef.current = setTimeout(() => {
      setIsVisible(true);
      // Calculate position after tooltip is rendered
      setTimeout(calculatePosition, 0);
    }, delay);
  };

  // Hide tooltip
  const hideTooltip = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    setIsVisible(false);
  };

  // Event handlers based on trigger type
  const getTriggerProps = () => {
    switch (trigger) {
      case 'hover':
        return {
          onMouseEnter: showTooltip,
          onMouseLeave: hideTooltip,
          onFocus: showTooltip,
          onBlur: hideTooltip
        };
      case 'click':
        return {
          onClick: () => isVisible ? hideTooltip() : showTooltip()
        };
      case 'focus':
        return {
          onFocus: showTooltip,
          onBlur: hideTooltip
        };
      default:
        return {};
    }
  };

  // Get theme classes
  const getThemeClasses = () => {
    const themes = {
      dark: 'bg-gray-900 text-white border-gray-700',
      light: 'bg-white text-gray-900 border-gray-200 shadow-lg',
      error: 'bg-red-500 text-white border-red-600',
      warning: 'bg-amber-500 text-white border-amber-600',
      success: 'bg-green-500 text-white border-green-600',
      info: 'bg-blue-500 text-white border-blue-600'
    };
    return themes[theme];
  };

  // Get arrow classes based on position
  const getArrowClasses = () => {
    const arrowBase = 'absolute w-2 h-2 transform rotate-45 border';
    const arrowTheme = theme === 'light' ? 'bg-white border-gray-200' : getThemeClasses().split(' ')[0] + ' border-current';
    
    switch (actualPosition) {
      case 'top':
        return `${arrowBase} ${arrowTheme} -bottom-1 left-1/2 -translate-x-1/2 border-t-0 border-l-0`;
      case 'bottom':
        return `${arrowBase} ${arrowTheme} -top-1 left-1/2 -translate-x-1/2 border-b-0 border-r-0`;
      case 'left':
        return `${arrowBase} ${arrowTheme} -right-1 top-1/2 -translate-y-1/2 border-l-0 border-b-0`;
      case 'right':
        return `${arrowBase} ${arrowTheme} -left-1 top-1/2 -translate-y-1/2 border-r-0 border-t-0`;
      default:
        return '';
    }
  };

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  // Update position on scroll/resize
  useEffect(() => {
    if (isVisible) {
      const handleUpdate = () => calculatePosition();
      window.addEventListener('scroll', handleUpdate, true);
      window.addEventListener('resize', handleUpdate);
      
      return () => {
        window.removeEventListener('scroll', handleUpdate, true);
        window.removeEventListener('resize', handleUpdate);
      };
    }
  }, [isVisible]);

  const tooltipContent = (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          ref={tooltipRef}
          style={tooltipStyle}
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.95 }}
          transition={{ duration: 0.15, ease: 'easeOut' }}
          className={`
            px-3 py-2 text-sm rounded-lg border backdrop-blur-sm
            ${getThemeClasses()}
            ${className}
          `}
          style={{
            ...tooltipStyle,
            maxWidth: `${maxWidth}px`
          }}
        >
          {content}
          {arrow && <div className={getArrowClasses()} />}
        </motion.div>
      )}
    </AnimatePresence>
  );

  return (
    <>
      <div
        ref={triggerRef}
        className="inline-block"
        {...getTriggerProps()}
      >
        {children}
      </div>
      {typeof window !== 'undefined' && createPortal(tooltipContent, document.body)}
    </>
  );
}

// Hook for programmatic tooltip control
export function useTooltip() {
  const [isVisible, setIsVisible] = useState(false);
  const [content, setContent] = useState<React.ReactNode>('');
  const [position, setPosition] = useState<{ x: number; y: number }>({ x: 0, y: 0 });

  const showTooltip = (newContent: React.ReactNode, x: number, y: number) => {
    setContent(newContent);
    setPosition({ x, y });
    setIsVisible(true);
  };

  const hideTooltip = () => {
    setIsVisible(false);
  };

  const TooltipComponent = () => (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.95 }}
          transition={{ duration: 0.15, ease: 'easeOut' }}
          className="fixed z-[9999] px-3 py-2 text-sm bg-gray-900 text-white rounded-lg border border-gray-700 backdrop-blur-sm pointer-events-none"
          style={{
            left: position.x,
            top: position.y,
            maxWidth: '200px'
          }}
        >
          {content}
        </motion.div>
      )}
    </AnimatePresence>
  );

  return {
    showTooltip,
    hideTooltip,
    TooltipComponent,
    isVisible
  };
}

// Utility component for quick tooltip usage
interface QuickTooltipProps {
  text: string;
  children: React.ReactNode;
  position?: 'top' | 'bottom' | 'left' | 'right' | 'auto';
  theme?: 'dark' | 'light' | 'error' | 'warning' | 'success' | 'info';
}

export function QuickTooltip({ text, children, position, theme }: QuickTooltipProps) {
  return (
    <Tooltip content={text} position={position} theme={theme}>
      {children}
    </Tooltip>
  );
}
