'use client';

import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface Tab {
  id: string;
  label: string;
  icon?: React.ReactNode;
  content: React.ReactNode;
}

interface TabbedNavigationProps {
  tabs: Tab[];
  defaultTab?: string;
  className?: string;
  variant?: 'default' | 'pills' | 'underline';
  size?: 'sm' | 'md' | 'lg';
  onTabChange?: (tabId: string) => void;
}

export function TabbedNavigation({ 
  tabs, 
  defaultTab,
  className = '',
  variant = 'underline',
  size = 'md',
  onTabChange
}: TabbedNavigationProps) {
  const [activeTab, setActiveTab] = useState(defaultTab || tabs[0]?.id);
  const [indicatorStyle, setIndicatorStyle] = useState({ width: 0, left: 0 });
  const tabsRef = useRef<(HTMLButtonElement | null)[]>([]);

  // Update indicator position when active tab changes
  useEffect(() => {
    const activeIndex = tabs.findIndex(tab => tab.id === activeTab);
    const activeTabElement = tabsRef.current[activeIndex];
    
    if (activeTabElement) {
      setIndicatorStyle({
        width: activeTabElement.offsetWidth,
        left: activeTabElement.offsetLeft,
      });
    }
  }, [activeTab, tabs]);

  const handleTabClick = (tabId: string) => {
    setActiveTab(tabId);
    onTabChange?.(tabId);
  };

  const sizeClasses = {
    sm: 'text-sm px-3 py-2',
    md: 'text-base px-4 py-3',
    lg: 'text-lg px-6 py-4'
  };

  const variantClasses = {
    default: 'border border-gray-200 dark:border-gray-700 rounded-lg',
    pills: '',
    underline: 'border-b border-gray-200 dark:border-gray-700'
  };

  return (
    <div className={`w-full ${className}`}>
      {/* Tab Navigation */}
      <div className={`relative ${variantClasses[variant]}`}>
        <nav className="flex space-x-1 relative" role="tablist">
          {tabs.map((tab, index) => {
            const isActive = activeTab === tab.id;
            
            return (
              <button
                key={tab.id}
                ref={(el) => (tabsRef.current[index] = el)}
                role="tab"
                aria-selected={isActive}
                aria-controls={`panel-${tab.id}`}
                onClick={() => handleTabClick(tab.id)}
                className={`
                  ${sizeClasses[size]}
                  relative z-10 font-medium transition-all duration-200 ease-in-out
                  focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:z-20
                  ${variant === 'pills' ? 'rounded-lg' : ''}
                  ${isActive 
                    ? variant === 'pills' 
                      ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/25' 
                      : 'text-blue-600 dark:text-blue-400'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
                  }
                  ${variant === 'pills' && !isActive ? 'hover:bg-gray-100 dark:hover:bg-gray-700' : ''}
                `}
              >
                <div className="flex items-center space-x-2">
                  {tab.icon && (
                    <span className={`transition-transform duration-200 ${isActive ? 'scale-110' : ''}`}>
                      {tab.icon}
                    </span>
                  )}
                  <span>{tab.label}</span>
                </div>
              </button>
            );
          })}
          
          {/* Sliding Underline Indicator */}
          {variant === 'underline' && (
            <motion.div
              className="absolute bottom-0 h-0.5 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full"
              style={{
                width: indicatorStyle.width,
                left: indicatorStyle.left,
              }}
              transition={{
                type: "spring",
                stiffness: 300,
                damping: 30,
              }}
            />
          )}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="mt-6">
        <AnimatePresence mode="wait">
          {tabs.map((tab) => {
            if (tab.id !== activeTab) return null;
            
            return (
              <motion.div
                key={tab.id}
                id={`panel-${tab.id}`}
                role="tabpanel"
                aria-labelledby={`tab-${tab.id}`}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.2, ease: "easeInOut" }}
                className="focus:outline-none"
              >
                {tab.content}
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>
    </div>
  );
}

export default TabbedNavigation;
