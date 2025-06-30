'use client';

import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { SkipForward, ArrowRight, Hash, Menu, Search, Settings, HelpCircle } from 'lucide-react';

interface SkipLink {
  id: string;
  href: string;
  label: string;
  description?: string;
  icon?: React.ComponentType<any>;
  priority: number;
  visible: boolean;
}

interface SkipLinksProps {
  customLinks?: Omit<SkipLink, 'id' | 'priority' | 'visible'>[];
  showOnFocusOnly?: boolean;
  position?: 'top-left' | 'top-center' | 'top-right';
  className?: string;
}

const defaultSkipLinks: Omit<SkipLink, 'id' | 'priority' | 'visible'>[] = [
  {
    href: '#main-content',
    label: 'Skip to main content',
    description: 'Jump directly to the main content area',
    icon: SkipForward
  },
  {
    href: '#navigation',
    label: 'Skip to navigation',
    description: 'Jump to the main navigation menu',
    icon: Menu
  },
  {
    href: '#search',
    label: 'Skip to search',
    description: 'Jump to the search functionality',
    icon: Search
  },
  {
    href: '#footer',
    label: 'Skip to footer',
    description: 'Jump to the footer content',
    icon: Hash
  }
];

export function SkipLinks({ 
  customLinks = [], 
  showOnFocusOnly = true,
  position = 'top-left',
  className = ''
}: SkipLinksProps) {
  const [isVisible, setIsVisible] = useState(!showOnFocusOnly);
  const [focusedIndex, setFocusedIndex] = useState(-1);
  const [availableTargets, setAvailableTargets] = useState<Set<string>>(new Set());
  const containerRef = useRef<HTMLDivElement>(null);

  // Combine default and custom links
  const allLinks: SkipLink[] = [
    ...defaultSkipLinks.map((link, index) => ({
      ...link,
      id: `skip-${index}`,
      priority: index,
      visible: true
    })),
    ...customLinks.map((link, index) => ({
      ...link,
      id: `custom-skip-${index}`,
      priority: defaultSkipLinks.length + index,
      visible: true
    }))
  ].sort((a, b) => a.priority - b.priority);

  // Check which target elements exist in the DOM
  useEffect(() => {
    const checkTargets = () => {
      const foundTargets = new Set<string>();
      allLinks.forEach(link => {
        const target = document.querySelector(link.href);
        if (target) {
          foundTargets.add(link.href);
        }
      });
      setAvailableTargets(foundTargets);
    };

    checkTargets();
    
    // Check again after a short delay to account for dynamic content
    const timeoutId = setTimeout(checkTargets, 1000);
    
    return () => clearTimeout(timeoutId);
  }, [allLinks]);

  // Filter links to only show those with available targets
  const visibleLinks = allLinks.filter(link => availableTargets.has(link.href));

  const positionClasses = {
    'top-left': 'top-0 left-0',
    'top-center': 'top-0 left-1/2 transform -translate-x-1/2',
    'top-right': 'top-0 right-0'
  };

  const handleFocus = () => {
    setIsVisible(true);
  };

  const handleBlur = (e: React.FocusEvent) => {
    // Hide when focus leaves the skip links container
    if (!containerRef.current?.contains(e.relatedTarget as Node)) {
      if (showOnFocusOnly) {
        setIsVisible(false);
      }
      setFocusedIndex(-1);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      if (showOnFocusOnly) {
        setIsVisible(false);
      }
      setFocusedIndex(-1);
      (document.activeElement as HTMLElement)?.blur();
    }
  };

  const handleSkipLinkClick = (href: string, label: string) => {
    const target = document.querySelector(href);
    if (target) {
      // Make the target focusable if it isn't already
      if (!target.hasAttribute('tabindex')) {
        target.setAttribute('tabindex', '-1');
      }
      
      // Focus the target
      (target as HTMLElement).focus();
      
      // Scroll to the target with smooth behavior
      target.scrollIntoView({ 
        behavior: 'smooth', 
        block: 'start' 
      });

      // Announce to screen readers
      const announcement = `Skipped to ${label}`;
      const announcer = document.createElement('div');
      announcer.setAttribute('aria-live', 'polite');
      announcer.setAttribute('aria-atomic', 'true');
      announcer.className = 'sr-only';
      announcer.textContent = announcement;
      document.body.appendChild(announcer);
      
      setTimeout(() => {
        document.body.removeChild(announcer);
      }, 1000);

      // Hide skip links after use if configured to do so
      if (showOnFocusOnly) {
        setIsVisible(false);
      }
    }
  };

  if (visibleLinks.length === 0) {
    return null;
  }

  return (
    <div
      ref={containerRef}
      className={`fixed ${positionClasses[position]} z-[9999] ${className}`}
      onBlur={handleBlur}
      onKeyDown={handleKeyDown}
    >
      <AnimatePresence>
        {(isVisible || !showOnFocusOnly) && (
          <motion.nav
            initial={{ opacity: 0, y: -50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -50 }}
            transition={{ duration: 0.2 }}
            role="navigation"
            aria-label="Skip navigation links"
            className="bg-gray-900 text-white shadow-lg rounded-b-lg border border-gray-700"
          >
            <div className="p-2">
              {/* Header */}
              <div className="px-3 py-2 text-xs font-medium text-gray-300 border-b border-gray-700">
                <div className="flex items-center space-x-2">
                  <SkipForward size={14} />
                  <span>Skip Links</span>
                </div>
              </div>

              {/* Skip Links */}
              <ul className="py-2 space-y-1" role="list">
                {visibleLinks.map((link, index) => {
                  const IconComponent = link.icon || ArrowRight;
                  return (
                    <li key={link.id} role="listitem">
                      <a
                        href={link.href}
                        onClick={(e) => {
                          e.preventDefault();
                          handleSkipLinkClick(link.href, link.label);
                        }}
                        onFocus={handleFocus}
                        onMouseEnter={() => setFocusedIndex(index)}
                        onMouseLeave={() => setFocusedIndex(-1)}
                        className={`
                          block px-3 py-2 text-sm transition-colors rounded-md
                          focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-offset-2 focus:ring-offset-gray-900
                          hover:bg-gray-800 focus:bg-gray-800
                          ${focusedIndex === index ? 'bg-gray-800' : ''}
                        `}
                        aria-describedby={link.description ? `${link.id}-desc` : undefined}
                      >
                        <div className="flex items-center space-x-3">
                          <IconComponent size={16} className="text-gray-400" />
                          <div className="flex-1">
                            <div className="text-white font-medium">
                              {link.label}
                            </div>
                            {link.description && (
                              <div 
                                id={`${link.id}-desc`}
                                className="text-xs text-gray-400 mt-1"
                              >
                                {link.description}
                              </div>
                            )}
                          </div>
                          <ArrowRight size={14} className="text-gray-500" />
                        </div>
                      </a>
                    </li>
                  );
                })}
              </ul>

              {/* Help Text */}
              <div className="px-3 py-2 text-xs text-gray-400 border-t border-gray-700">
                <div className="flex items-center space-x-1">
                  <HelpCircle size={12} />
                  <span>Press Escape to hide</span>
                </div>
              </div>
            </div>
          </motion.nav>
        )}
      </AnimatePresence>
    </div>
  );
}

// Component to automatically add skip targets to page sections
interface SkipTargetProps {
  id: string;
  children: React.ReactNode;
  label?: string;
  className?: string;
}

export function SkipTarget({ id, children, label, className = '' }: SkipTargetProps) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const element = ref.current;
    if (element) {
      // Ensure the element can receive focus
      if (!element.hasAttribute('tabindex')) {
        element.setAttribute('tabindex', '-1');
      }

      // Add aria-label if provided
      if (label) {
        element.setAttribute('aria-label', label);
      }

      // Add role if not already present
      if (!element.hasAttribute('role')) {
        element.setAttribute('role', 'region');
      }
    }
  }, [label]);

  return (
    <div
      ref={ref}
      id={id}
      className={`focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded-md ${className}`}
    >
      {children}
    </div>
  );
}

// Hook to programmatically register skip links
export function useSkipLink(href: string, label: string, description?: string) {
  useEffect(() => {
    const target = document.querySelector(href);
    if (target && !target.hasAttribute('tabindex')) {
      target.setAttribute('tabindex', '-1');
    }
  }, [href]);

  const skip = () => {
    const target = document.querySelector(href);
    if (target) {
      (target as HTMLElement).focus();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  return skip;
}

// Main layout wrapper that includes common skip targets
interface AccessiblePageLayoutProps {
  children: React.ReactNode;
  skipLinks?: Omit<SkipLink, 'id' | 'priority' | 'visible'>[];
  showSkipLinks?: boolean;
}

export function AccessiblePageLayout({ 
  children, 
  skipLinks = [],
  showSkipLinks = true 
}: AccessiblePageLayoutProps) {
  return (
    <div className="min-h-screen">
      {/* Skip Links */}
      {showSkipLinks && <SkipLinks customLinks={skipLinks} />}
      
      {/* Page Content */}
      {children}
    </div>
  );
}

// Utility to create landmark regions with skip targets
interface LandmarkProps {
  as?: keyof JSX.IntrinsicElements;
  id: string;
  label: string;
  children: React.ReactNode;
  className?: string;
}

export function Landmark({ 
  as: Component = 'div', 
  id, 
  label, 
  children, 
  className = '' 
}: LandmarkProps) {
  const ref = useRef<HTMLElement>(null);

  useEffect(() => {
    const element = ref.current;
    if (element) {
      element.setAttribute('tabindex', '-1');
      element.setAttribute('aria-label', label);
    }
  }, [label]);

  return (
    <Component
      ref={ref}
      id={id}
      className={`focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded-md ${className}`}
    >
      {children}
    </Component>
  );
}

// CSS to be added to globals.css
export const skipLinksStyles = `
/* Skip Links Styles */
.skip-link {
  position: absolute;
  top: -40px;
  left: 6px;
  background: #1f2937;
  color: #fff;
  padding: 8px 12px;
  text-decoration: none;
  border-radius: 4px;
  z-index: 9999;
  transition: top 0.3s ease;
  font-size: 14px;
  font-weight: 500;
}

.skip-link:focus {
  top: 6px;
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}

/* High contrast mode skip links */
[data-high-contrast="true"] .skip-link {
  background: var(--high-contrast-bg);
  color: var(--high-contrast-fg);
  border: 2px solid var(--high-contrast-border);
}

[data-high-contrast="true"] .skip-link:focus {
  outline: 3px solid var(--high-contrast-focus);
}

/* Skip target focus styles */
[id]:target {
  scroll-margin-top: 2rem;
}

/* Screen reader only text for skip targets */
.skip-target-label {
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

/* Focus styles for skip targets */
[tabindex="-1"]:focus {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
  border-radius: 4px;
}

/* Smooth scrolling for skip links */
html {
  scroll-behavior: smooth;
}

/* Ensure skip targets are visible when focused */
[tabindex="-1"]:focus {
  scroll-margin-top: 1rem;
}
`;
