'use client';

import React, { useState, useEffect, createContext, useContext } from 'react';
import { motion } from 'framer-motion';
import { Monitor, Sun, Moon, Contrast, Eye, Palette } from 'lucide-react';

type ThemeMode = 'light' | 'dark' | 'high-contrast-light' | 'high-contrast-dark' | 'auto';

interface HighContrastContextType {
  themeMode: ThemeMode;
  setThemeMode: (mode: ThemeMode) => void;
  isHighContrast: boolean;
  toggleHighContrast: () => void;
  contrastRatio: number;
  setContrastRatio: (ratio: number) => void;
}

const HighContrastContext = createContext<HighContrastContextType | undefined>(undefined);

export function useHighContrast() {
  const context = useContext(HighContrastContext);
  if (!context) {
    throw new Error('useHighContrast must be used within a HighContrastProvider');
  }
  return context;
}

interface HighContrastProviderProps {
  children: React.ReactNode;
}

export function HighContrastProvider({ children }: HighContrastProviderProps) {
  const [themeMode, setThemeMode] = useState<ThemeMode>('auto');
  const [contrastRatio, setContrastRatio] = useState(7); // WCAG AAA standard

  const isHighContrast = themeMode.includes('high-contrast');

  useEffect(() => {
    // Load saved theme from localStorage
    const savedTheme = localStorage.getItem('theme-mode') as ThemeMode;
    const savedContrast = localStorage.getItem('contrast-ratio');
    
    if (savedTheme) {
      setThemeMode(savedTheme);
    }
    
    if (savedContrast) {
      setContrastRatio(Number(savedContrast));
    }
  }, []);

  useEffect(() => {
    // Apply theme to document
    const root = document.documentElement;
    const body = document.body;
    
    // Remove all theme classes
    root.classList.remove('light', 'dark', 'high-contrast-light', 'high-contrast-dark');
    body.classList.remove('light', 'dark', 'high-contrast-light', 'high-contrast-dark');
    
    // Apply current theme
    if (themeMode === 'auto') {
      const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      const autoTheme = isDark ? 'dark' : 'light';
      root.classList.add(autoTheme);
      body.classList.add(autoTheme);
    } else {
      root.classList.add(themeMode);
      body.classList.add(themeMode);
    }

    // Apply high contrast CSS variables
    if (isHighContrast) {
      root.style.setProperty('--contrast-ratio', contrastRatio.toString());
      root.setAttribute('data-high-contrast', 'true');
    } else {
      root.removeAttribute('data-high-contrast');
    }

    // Save to localStorage
    localStorage.setItem('theme-mode', themeMode);
    localStorage.setItem('contrast-ratio', contrastRatio.toString());
  }, [themeMode, contrastRatio, isHighContrast]);

  const toggleHighContrast = () => {
    if (isHighContrast) {
      // Switch to regular mode
      setThemeMode(prev => 
        prev === 'high-contrast-light' ? 'light' : 
        prev === 'high-contrast-dark' ? 'dark' : 'auto'
      );
    } else {
      // Switch to high contrast mode
      setThemeMode(prev => 
        prev === 'light' ? 'high-contrast-light' :
        prev === 'dark' ? 'high-contrast-dark' :
        'high-contrast-light' // default for auto
      );
    }
  };

  return (
    <HighContrastContext.Provider 
      value={{
        themeMode,
        setThemeMode,
        isHighContrast,
        toggleHighContrast,
        contrastRatio,
        setContrastRatio
      }}
    >
      {children}
    </HighContrastContext.Provider>
  );
}

interface HighContrastToggleProps {
  showLabel?: boolean;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function HighContrastToggle({ 
  showLabel = true, 
  size = 'md',
  className = '' 
}: HighContrastToggleProps) {
  const { themeMode, setThemeMode, isHighContrast, contrastRatio, setContrastRatio } = useHighContrast();
  const [showSettings, setShowSettings] = useState(false);

  const sizeClasses = {
    sm: 'p-2 text-sm',
    md: 'p-3 text-base',
    lg: 'p-4 text-lg'
  };

  const iconSizes = {
    sm: 16,
    md: 20,
    lg: 24
  };

  const getThemeIcon = () => {
    switch (themeMode) {
      case 'light':
        return <Sun size={iconSizes[size]} />;
      case 'dark':
        return <Moon size={iconSizes[size]} />;
      case 'high-contrast-light':
      case 'high-contrast-dark':
        return <Contrast size={iconSizes[size]} />;
      case 'auto':
      default:
        return <Monitor size={iconSizes[size]} />;
    }
  };

  const getThemeLabel = () => {
    switch (themeMode) {
      case 'light':
        return 'Light Mode';
      case 'dark':
        return 'Dark Mode';
      case 'high-contrast-light':
        return 'High Contrast Light';
      case 'high-contrast-dark':
        return 'High Contrast Dark';
      case 'auto':
      default:
        return 'Auto Mode';
    }
  };

  const themeOptions: Array<{ mode: ThemeMode; label: string; icon: React.ReactNode }> = [
    { mode: 'auto', label: 'Auto', icon: <Monitor size={16} /> },
    { mode: 'light', label: 'Light', icon: <Sun size={16} /> },
    { mode: 'dark', label: 'Dark', icon: <Moon size={16} /> },
    { mode: 'high-contrast-light', label: 'High Contrast Light', icon: <Contrast size={16} /> },
    { mode: 'high-contrast-dark', label: 'High Contrast Dark', icon: <Contrast size={16} /> },
  ];

  return (
    <div className={`relative ${className}`}>
      <div className="flex items-center space-x-2">
        {/* Theme Selector Dropdown */}
        <div className="relative">
          <motion.button
            onClick={() => setShowSettings(!showSettings)}
            className={`
              ${sizeClasses[size]}
              flex items-center space-x-2
              bg-white dark:bg-gray-800 
              border border-gray-300 dark:border-gray-600
              hover:border-gray-400 dark:hover:border-gray-500
              rounded-lg transition-colors
              text-gray-700 dark:text-gray-300
              hover:text-gray-900 dark:hover:text-white
              focus:ring-2 focus:ring-blue-500 focus:border-blue-500
              ${isHighContrast ? 'ring-2 ring-yellow-500' : ''}
            `}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            aria-label={`Current theme: ${getThemeLabel()}. Click to change theme.`}
            aria-expanded={showSettings}
            aria-haspopup="menu"
          >
            {getThemeIcon()}
            {showLabel && (
              <span className="font-medium">
                {getThemeLabel()}
              </span>
            )}
          </motion.button>

          {/* Theme Options Dropdown */}
          {showSettings && (
            <motion.div
              initial={{ opacity: 0, y: -10, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -10, scale: 0.95 }}
              className="absolute top-full mt-2 right-0 z-50 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg py-2 min-w-48"
              role="menu"
              aria-label="Theme options"
            >
              {themeOptions.map((option) => (
                <button
                  key={option.mode}
                  onClick={() => {
                    setThemeMode(option.mode);
                    setShowSettings(false);
                  }}
                  className={`
                    w-full px-4 py-2 text-left flex items-center space-x-3
                    hover:bg-gray-100 dark:hover:bg-gray-700
                    text-gray-700 dark:text-gray-300
                    ${themeMode === option.mode ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300' : ''}
                  `}
                  role="menuitem"
                  aria-current={themeMode === option.mode}
                >
                  {option.icon}
                  <span>{option.label}</span>
                  {themeMode === option.mode && (
                    <span className="ml-auto text-blue-500">✓</span>
                  )}
                </button>
              ))}
              
              {/* High Contrast Settings */}
              {isHighContrast && (
                <>
                  <hr className="my-2 border-gray-200 dark:border-gray-700" />
                  <div className="px-4 py-2">
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Contrast Ratio: {contrastRatio}:1
                    </label>
                    <input
                      type="range"
                      min="4.5"
                      max="21"
                      step="0.5"
                      value={contrastRatio}
                      onChange={(e) => setContrastRatio(Number(e.target.value))}
                      className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
                      aria-label={`Contrast ratio: ${contrastRatio} to 1`}
                    />
                    <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
                      <span>AA (4.5:1)</span>
                      <span>AAA (7:1)</span>
                      <span>Max (21:1)</span>
                    </div>
                  </div>
                </>
              )}
            </motion.div>
          )}
        </div>

        {/* Quick High Contrast Toggle */}
        <motion.button
          onClick={() => {
            if (isHighContrast) {
              setThemeMode(prev => 
                prev === 'high-contrast-light' ? 'light' : 
                prev === 'high-contrast-dark' ? 'dark' : 'auto'
              );
            } else {
              setThemeMode(prev => 
                prev === 'light' ? 'high-contrast-light' :
                prev === 'dark' ? 'high-contrast-dark' :
                'high-contrast-light'
              );
            }
          }}
          className={`
            ${sizeClasses[size]}
            flex items-center justify-center
            ${isHighContrast 
              ? 'bg-yellow-500 text-black hover:bg-yellow-400' 
              : 'bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-400 hover:bg-gray-300 dark:hover:bg-gray-600'
            }
            rounded-lg transition-colors
            focus:ring-2 focus:ring-blue-500
          `}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          aria-label={`${isHighContrast ? 'Disable' : 'Enable'} high contrast mode`}
          aria-pressed={isHighContrast}
        >
          <Eye size={iconSizes[size]} />
        </motion.button>
      </div>

      {/* Accessibility Info */}
      {isHighContrast && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className="mt-2 p-2 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-700 rounded text-xs text-yellow-800 dark:text-yellow-200"
        >
          <div className="flex items-center space-x-1">
            <Eye size={12} />
            <span>
              High contrast mode active (Ratio: {contrastRatio}:1) 
              {contrastRatio >= 7 ? ' - WCAG AAA compliant' : contrastRatio >= 4.5 ? ' - WCAG AA compliant' : ''}
            </span>
          </div>
        </motion.div>
      )}

      {/* Click outside handler */}
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

// CSS to be added to globals.css
export const highContrastStyles = `
/* High Contrast Mode Styles */
[data-high-contrast="true"] {
  --high-contrast-bg: #000000;
  --high-contrast-fg: #ffffff;
  --high-contrast-border: #ffffff;
  --high-contrast-focus: #ffff00;
  --high-contrast-link: #00ffff;
  --high-contrast-visited: #ff00ff;
  --high-contrast-error: #ff0000;
  --high-contrast-success: #00ff00;
  --high-contrast-warning: #ffff00;
}

.high-contrast-light {
  --high-contrast-bg: #ffffff;
  --high-contrast-fg: #000000;
  --high-contrast-border: #000000;
  --high-contrast-focus: #0000ff;
  --high-contrast-link: #0000ff;
  --high-contrast-visited: #800080;
  --high-contrast-error: #ff0000;
  --high-contrast-success: #008000;
  --high-contrast-warning: #ff8c00;
}

.high-contrast-dark {
  --high-contrast-bg: #000000;
  --high-contrast-fg: #ffffff;
  --high-contrast-border: #ffffff;
  --high-contrast-focus: #ffff00;
  --high-contrast-link: #00ffff;
  --high-contrast-visited: #ff00ff;
  --high-contrast-error: #ff4444;
  --high-contrast-success: #44ff44;
  --high-contrast-warning: #ffff44;
}

/* Apply high contrast styles when enabled */
[data-high-contrast="true"] * {
  background-color: var(--high-contrast-bg) !important;
  color: var(--high-contrast-fg) !important;
  border-color: var(--high-contrast-border) !important;
}

[data-high-contrast="true"] a {
  color: var(--high-contrast-link) !important;
}

[data-high-contrast="true"] a:visited {
  color: var(--high-contrast-visited) !important;
}

[data-high-contrast="true"] *:focus {
  outline: 3px solid var(--high-contrast-focus) !important;
  outline-offset: 2px !important;
}

[data-high-contrast="true"] button,
[data-high-contrast="true"] input,
[data-high-contrast="true"] select,
[data-high-contrast="true"] textarea {
  border: 2px solid var(--high-contrast-border) !important;
}

[data-high-contrast="true"] .error {
  color: var(--high-contrast-error) !important;
}

[data-high-contrast="true"] .success {
  color: var(--high-contrast-success) !important;
}

[data-high-contrast="true"] .warning {
  color: var(--high-contrast-warning) !important;
}

/* Slider styles for high contrast */
[data-high-contrast="true"] .slider::-webkit-slider-thumb {
  background: var(--high-contrast-fg) !important;
  border: 2px solid var(--high-contrast-border) !important;
}

[data-high-contrast="true"] .slider::-moz-range-thumb {
  background: var(--high-contrast-fg) !important;
  border: 2px solid var(--high-contrast-border) !important;
}
`;
