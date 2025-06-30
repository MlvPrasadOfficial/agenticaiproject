'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Home, FileText, BarChart3, MessageSquare, Zap, Settings,
  ChevronLeft, ChevronRight, User, Bell, LogOut, Shield,
  Briefcase
} from 'lucide-react';

interface SidebarProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
  className?: string;
}

interface NavItem {
  id: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: string;
  badgeColor?: string;
  disabled?: boolean;
  description?: string;
}

export default function GlassmorphismSidebar({ activeTab, onTabChange, className = '' }: SidebarProps) {
  const [isCollapsed, setIsCollapsed] = useState(false);

  const navigationItems: NavItem[] = [
    { 
      id: 'dashboard', 
      label: 'Dashboard', 
      icon: Home,
      description: 'Overview and analytics'
    },
    { 
      id: 'upload', 
      label: 'Data Upload', 
      icon: FileText,
      description: 'Import and manage data'
    },
    { 
      id: 'data', 
      label: 'Analytics', 
      icon: BarChart3,
      badge: 'Pro',
      badgeColor: 'bg-gradient-to-r from-blue-500 to-indigo-600',
      description: 'Advanced data analysis'
    },
    { 
      id: 'chat', 
      label: 'AI Assistant', 
      icon: MessageSquare,
      badge: 'AI',
      badgeColor: 'bg-gradient-to-r from-purple-500 to-violet-600',
      description: 'Intelligent conversations'
    },
    { 
      id: 'insights', 
      label: 'Insights', 
      icon: Zap,
      badge: 'New',
      badgeColor: 'bg-gradient-to-r from-green-500 to-emerald-600',
      description: 'Business intelligence'
    },
    { 
      id: 'settings', 
      label: 'Settings', 
      icon: Settings,
      description: 'System configuration'
    },
  ];

  const handleItemClick = (itemId: string, disabled?: boolean) => {
    if (disabled) return;
    onTabChange(itemId);
  };

  const handleToggleCollapse = () => {
    setIsCollapsed(!isCollapsed);
  };

  const handleKeyDown = (event: React.KeyboardEvent, itemId: string, disabled?: boolean) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      handleItemClick(itemId, disabled);
    }
  };

  return (
    <motion.aside
      initial={false}
      animate={{ width: isCollapsed ? 80 : 280 }}
      transition={{ duration: 0.3, ease: "easeInOut" }}
      className={`fixed left-0 top-0 h-full bg-white/95 dark:bg-slate-900/95 backdrop-blur-xl border-r border-slate-200/50 dark:border-slate-700/50 z-50 shadow-2xl ${className}`}
    >
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-5">
        <div className="absolute inset-0" style={{
          backgroundImage: `linear-gradient(45deg, rgba(59, 130, 246, 0.1) 25%, transparent 25%), 
                           linear-gradient(-45deg, rgba(59, 130, 246, 0.1) 25%, transparent 25%), 
                           linear-gradient(45deg, transparent 75%, rgba(59, 130, 246, 0.1) 75%), 
                           linear-gradient(-45deg, transparent 75%, rgba(59, 130, 246, 0.1) 75%)`,
          backgroundSize: '20px 20px',
          backgroundPosition: '0 0, 0 10px, 10px -10px, -10px 0px'
        }} />
      </div>

      <div className="relative h-full flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-slate-200/50 dark:border-slate-700/50">
          <AnimatePresence mode="wait">
            {!isCollapsed && (
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.2 }}
                className="flex items-center space-x-3"
              >
                <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-xl flex items-center justify-center shadow-lg">
                  <Briefcase className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h1 className="text-lg font-bold bg-gradient-to-r from-slate-900 to-slate-600 dark:from-white dark:to-slate-300 bg-clip-text text-transparent">
                    Enterprise
                  </h1>
                  <p className="text-xs text-slate-600 dark:text-slate-400 font-medium">
                    Insights Platform
                  </p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
          
          <button
            onClick={handleToggleCollapse}
            className="p-2 rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 transition-all duration-200 shadow-sm"
            aria-label={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            {isCollapsed ? (
              <ChevronRight className="w-4 h-4 text-slate-600 dark:text-slate-400" />
            ) : (
              <ChevronLeft className="w-4 h-4 text-slate-600 dark:text-slate-400" />
            )}
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-4 py-6">
          <ul className="space-y-2">
            {navigationItems.map((item, index) => {
              const isActive = activeTab === item.id;
              const Icon = item.icon;
              
              return (
                <motion.li
                  key={item.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.05 }}
                >
                  <button
                    onClick={() => handleItemClick(item.id, item.disabled)}
                    onKeyDown={(e) => handleKeyDown(e, item.id, item.disabled)}
                    disabled={item.disabled}
                    className={`
                      relative w-full flex items-center px-4 py-3 rounded-xl text-left transition-all duration-200 group
                      ${isActive 
                        ? 'bg-gradient-to-r from-blue-500 to-indigo-600 text-white shadow-lg shadow-blue-500/25' 
                        : 'text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800/50'
                      }
                      ${item.disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
                      ${isCollapsed ? 'justify-center' : ''}
                    `}
                    title={isCollapsed ? item.label : ''}
                  >
                    {/* Active indicator */}
                    {isActive && (
                      <motion.div
                        layoutId="activeTab"
                        className="absolute inset-0 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-xl"
                        transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                      />
                    )}
                    
                    {/* Content */}
                    <div className="relative flex items-center w-full">
                      <div className={`
                        flex-shrink-0 p-2 rounded-lg transition-all duration-200
                        ${isActive 
                          ? 'bg-white/20' 
                          : 'bg-slate-100 dark:bg-slate-800 group-hover:bg-slate-200 dark:group-hover:bg-slate-700'
                        }
                      `}>
                        <Icon className={`w-5 h-5 ${isActive ? 'text-white' : 'text-slate-600 dark:text-slate-400'}`} />
                      </div>
                      
                      <AnimatePresence mode="wait">
                        {!isCollapsed && (
                          <motion.div
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -10 }}
                            transition={{ duration: 0.2 }}
                            className="ml-4 flex-1 min-w-0"
                          >
                            <div className="flex items-center justify-between">
                              <div>
                                <span className={`block font-semibold text-sm ${isActive ? 'text-white' : ''}`}>
                                  {item.label}
                                </span>
                                <span className={`block text-xs mt-0.5 ${
                                  isActive 
                                    ? 'text-white/80' 
                                    : 'text-slate-500 dark:text-slate-500'
                                }`}>
                                  {item.description}
                                </span>
                              </div>
                              
                              {item.badge && (
                                <span className={`
                                  px-2 py-1 text-xs font-bold text-white rounded-full shadow-sm
                                  ${item.badgeColor || 'bg-gradient-to-r from-blue-500 to-indigo-600'}
                                `}>
                                  {item.badge}
                                </span>
                              )}
                            </div>
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </div>
                  </button>
                </motion.li>
              );
            })}
          </ul>
        </nav>

        {/* User Profile Section */}
        <div className="border-t border-slate-200/50 dark:border-slate-700/50 p-4">
          <AnimatePresence mode="wait">
            {!isCollapsed ? (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 10 }}
                transition={{ duration: 0.2 }}
                className="space-y-3"
              >
                {/* User Info */}
                <div className="flex items-center space-x-3 p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50">
                  <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-emerald-600 rounded-full flex items-center justify-center shadow-lg">
                    <User className="w-5 h-5 text-white" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold text-slate-900 dark:text-slate-100 truncate">
                      Enterprise User
                    </p>
                    <p className="text-xs text-slate-500 dark:text-slate-400 truncate">
                      admin@company.com
                    </p>
                  </div>
                </div>
                
                {/* Quick Actions */}
                <div className="flex space-x-2">
                  <button className="flex-1 flex items-center justify-center p-2 rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors duration-200">
                    <Bell className="w-4 h-4 text-slate-600 dark:text-slate-400" />
                  </button>
                  <button className="flex-1 flex items-center justify-center p-2 rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors duration-200">
                    <Shield className="w-4 h-4 text-slate-600 dark:text-slate-400" />
                  </button>
                  <button className="flex-1 flex items-center justify-center p-2 rounded-lg bg-red-100 dark:bg-red-900/20 hover:bg-red-200 dark:hover:bg-red-900/40 transition-colors duration-200">
                    <LogOut className="w-4 h-4 text-red-600 dark:text-red-400" />
                  </button>
                </div>
              </motion.div>
            ) : (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.2 }}
                className="flex flex-col space-y-2"
              >
                <button className="p-3 rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors duration-200">
                  <User className="w-5 h-5 text-slate-600 dark:text-slate-400" />
                </button>
                <button className="p-3 rounded-lg bg-red-100 dark:bg-red-900/20 hover:bg-red-200 dark:hover:bg-red-900/40 transition-colors duration-200">
                  <LogOut className="w-5 h-5 text-red-600 dark:text-red-400" />
                </button>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </motion.aside>
  );
}
