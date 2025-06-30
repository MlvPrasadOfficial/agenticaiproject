'use client';

import React from 'react';
import { motion } from 'framer-motion';

interface ToggleSwitchProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  label?: string;
  description?: string;
  disabled?: boolean;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'default' | 'success' | 'warning' | 'danger';
  className?: string;
  showIcons?: boolean;
  loading?: boolean;
}

export function ToggleSwitch({
  checked,
  onChange,
  label,
  description,
  disabled = false,
  size = 'md',
  variant = 'default',
  className = '',
  showIcons = false,
  loading = false
}: ToggleSwitchProps) {
  const handleToggle = () => {
    if (!disabled && !loading) {
      onChange(!checked);
    }
  };

  const sizeConfig = {
    sm: {
      track: 'w-8 h-4',
      thumb: 'w-3 h-3',
      translate: checked ? 'translate-x-4' : 'translate-x-0.5',
      icon: 'w-2 h-2'
    },
    md: {
      track: 'w-11 h-6',
      thumb: 'w-5 h-5',
      translate: checked ? 'translate-x-5' : 'translate-x-0.5',
      icon: 'w-3 h-3'
    },
    lg: {
      track: 'w-14 h-7',
      thumb: 'w-6 h-6',
      translate: checked ? 'translate-x-7' : 'translate-x-0.5',
      icon: 'w-4 h-4'
    }
  };

  const variantConfig = {
    default: {
      trackOn: 'bg-blue-600',
      trackOff: 'bg-gray-200 dark:bg-gray-700',
      thumb: 'bg-white shadow-lg'
    },
    success: {
      trackOn: 'bg-green-600',
      trackOff: 'bg-gray-200 dark:bg-gray-700',
      thumb: 'bg-white shadow-lg'
    },
    warning: {
      trackOn: 'bg-yellow-500',
      trackOff: 'bg-gray-200 dark:bg-gray-700',
      thumb: 'bg-white shadow-lg'
    },
    danger: {
      trackOn: 'bg-red-600',
      trackOff: 'bg-gray-200 dark:bg-gray-700',
      thumb: 'bg-white shadow-lg'
    }
  };

  const config = sizeConfig[size];
  const colors = variantConfig[variant];

  return (
    <div className={`flex items-start space-x-3 ${className}`}>
      {/* Toggle Switch */}
      <button
        type="button"
        role="switch"
        aria-checked={checked}
        aria-label={label || 'Toggle switch'}
        onClick={handleToggle}
        disabled={disabled || loading}
        className={`
          ${config.track}
          relative inline-flex items-center rounded-full transition-colors duration-200 ease-in-out
          focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:ring-offset-2 dark:focus:ring-offset-gray-800
          ${checked ? colors.trackOn : colors.trackOff}
          ${disabled || loading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
        `}
      >
        {/* Thumb */}
        <motion.span
          layout
          transition={{
            type: "spring",
            stiffness: 500,
            damping: 30
          }}
          className={`
            ${config.thumb}
            inline-block rounded-full ${colors.thumb}
            transform transition-transform duration-200 ease-in-out
            ${config.translate}
            ${loading ? 'animate-pulse' : ''}
          `}
        >
          {/* Icons */}
          {showIcons && !loading && (
            <motion.div
              initial={{ opacity: 0, scale: 0.5 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.5 }}
              transition={{ duration: 0.15 }}
              className="flex items-center justify-center w-full h-full"
            >
              {checked ? (
                <svg
                  className={`${config.icon} text-blue-600`}
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                    clipRule="evenodd"
                  />
                </svg>
              ) : (
                <svg
                  className={`${config.icon} text-gray-400`}
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                    clipRule="evenodd"
                  />
                </svg>
              )}
            </motion.div>
          )}

          {/* Loading Indicator */}
          {loading && (
            <div className="flex items-center justify-center w-full h-full">
              <div className={`${config.icon.replace('w-', 'w-').replace('h-', 'h-')} animate-spin rounded-full border-2 border-gray-300 border-t-blue-600`} />
            </div>
          )}
        </motion.span>
      </button>

      {/* Label and Description */}
      {(label || description) && (
        <div className="flex-1 min-w-0">
          {label && (
            <label
              htmlFor={undefined}
              className={`
                block text-sm font-medium text-gray-900 dark:text-gray-100
                ${disabled ? 'opacity-50' : 'cursor-pointer'}
              `}
              onClick={handleToggle}
            >
              {label}
            </label>
          )}
          {description && (
            <p className={`
              mt-1 text-sm text-gray-500 dark:text-gray-400
              ${disabled ? 'opacity-50' : ''}
            `}>
              {description}
            </p>
          )}
        </div>
      )}
    </div>
  );
}

// Toggle Group Component for multiple related toggles
interface ToggleGroupProps {
  title?: string;
  description?: string;
  children: React.ReactNode;
  className?: string;
}

export function ToggleGroup({ title, description, children, className = '' }: ToggleGroupProps) {
  return (
    <div className={`space-y-4 ${className}`}>
      {(title || description) && (
        <div>
          {title && (
            <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">
              {title}
            </h3>
          )}
          {description && (
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              {description}
            </p>
          )}
        </div>
      )}
      <div className="space-y-3">
        {children}
      </div>
    </div>
  );
}

export default ToggleSwitch;
