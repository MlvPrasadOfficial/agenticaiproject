'use client';

import React, { useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, AlertCircle, CheckCircle, Info, AlertTriangle } from 'lucide-react';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
  variant?: 'default' | 'success' | 'warning' | 'error' | 'info';
  showCloseButton?: boolean;
  closeOnBackdropClick?: boolean;
  closeOnEscape?: boolean;
  className?: string;
  headerClassName?: string;
  bodyClassName?: string;
  footerClassName?: string;
  preventBodyScroll?: boolean;
}

const variantConfig = {
  default: {
    icon: null,
    headerBg: 'bg-white dark:bg-gray-800',
    iconColor: 'text-gray-600'
  },
  success: {
    icon: CheckCircle,
    headerBg: 'bg-green-50 dark:bg-green-900/20',
    iconColor: 'text-green-600 dark:text-green-400'
  },
  warning: {
    icon: AlertTriangle,
    headerBg: 'bg-yellow-50 dark:bg-yellow-900/20',
    iconColor: 'text-yellow-600 dark:text-yellow-400'
  },
  error: {
    icon: AlertCircle,
    headerBg: 'bg-red-50 dark:bg-red-900/20',
    iconColor: 'text-red-600 dark:text-red-400'
  },
  info: {
    icon: Info,
    headerBg: 'bg-blue-50 dark:bg-blue-900/20',
    iconColor: 'text-blue-600 dark:text-blue-400'
  }
};

const sizeConfig = {
  sm: 'max-w-md',
  md: 'max-w-lg',
  lg: 'max-w-2xl',
  xl: 'max-w-4xl',
  full: 'max-w-full mx-4'
};

export function Modal({
  isOpen,
  onClose,
  title,
  children,
  size = 'md',
  variant = 'default',
  showCloseButton = true,
  closeOnBackdropClick = true,
  closeOnEscape = true,
  className = '',
  headerClassName = '',
  bodyClassName = '',
  footerClassName = '',
  preventBodyScroll = true
}: ModalProps) {
  const modalRef = useRef<HTMLDivElement>(null);
  const config = variantConfig[variant];
  const IconComponent = config.icon;

  // Handle body scroll prevention
  useEffect(() => {
    if (preventBodyScroll && isOpen) {
      document.body.style.overflow = 'hidden';
      return () => {
        document.body.style.overflow = 'unset';
      };
    }
  }, [isOpen, preventBodyScroll]);

  // Handle escape key
  useEffect(() => {
    if (closeOnEscape) {
      const handleEscape = (event: KeyboardEvent) => {
        if (event.key === 'Escape' && isOpen) {
          onClose();
        }
      };

      document.addEventListener('keydown', handleEscape);
      return () => document.removeEventListener('keydown', handleEscape);
    }
  }, [isOpen, onClose, closeOnEscape]);

  // Focus management
  useEffect(() => {
    if (isOpen && modalRef.current) {
      modalRef.current.focus();
    }
  }, [isOpen]);

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (closeOnBackdropClick && e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.2 }}
          className="fixed inset-0 z-50 overflow-y-auto"
          role="dialog"
          aria-modal="true"
          aria-labelledby={title ? 'modal-title' : undefined}
        >
          {/* Backdrop with blur effect */}
          <div
            className="fixed inset-0 bg-black/50 backdrop-blur-sm"
            onClick={handleBackdropClick}
          />

          {/* Modal Container */}
          <div className="flex min-h-full items-center justify-center p-4">
            <motion.div
              ref={modalRef}
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              transition={{ 
                type: "spring",
                stiffness: 300,
                damping: 30 
              }}
              className={`
                relative w-full ${sizeConfig[size]}
                bg-white dark:bg-gray-800 rounded-2xl shadow-2xl
                border border-gray-200 dark:border-gray-700
                overflow-hidden
                ${className}
              `}
              tabIndex={-1}
            >
              {/* Header */}
              {(title || showCloseButton) && (
                <div className={`
                  px-6 py-4 border-b border-gray-200 dark:border-gray-700
                  ${config.headerBg} ${headerClassName}
                `}>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      {IconComponent && (
                        <IconComponent className={`w-6 h-6 ${config.iconColor}`} />
                      )}
                      {title && (
                        <h2 
                          id="modal-title"
                          className="text-lg font-semibold text-gray-900 dark:text-gray-100"
                        >
                          {title}
                        </h2>
                      )}
                    </div>
                    
                    {showCloseButton && (
                      <button
                        onClick={onClose}
                        className="p-1 rounded-lg text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                        aria-label="Close modal"
                      >
                        <X className="w-5 h-5" />
                      </button>
                    )}
                  </div>
                </div>
              )}

              {/* Body */}
              <div className={`px-6 py-4 ${bodyClassName}`}>
                {children}
              </div>
            </motion.div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

// Modal Footer Component
export function ModalFooter({ 
  children, 
  className = '',
  justify = 'end' 
}: { 
  children: React.ReactNode; 
  className?: string;
  justify?: 'start' | 'center' | 'end' | 'between';
}) {
  const justifyClasses = {
    start: 'justify-start',
    center: 'justify-center',
    end: 'justify-end',
    between: 'justify-between'
  };

  return (
    <div className={`
      px-6 py-4 border-t border-gray-200 dark:border-gray-700
      bg-gray-50 dark:bg-gray-900/50
      flex items-center space-x-3 ${justifyClasses[justify]}
      ${className}
    `}>
      {children}
    </div>
  );
}

// Confirmation Modal Component
interface ConfirmationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  variant?: 'default' | 'success' | 'warning' | 'error';
  loading?: boolean;
}

export function ConfirmationModal({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  variant = 'default',
  loading = false
}: ConfirmationModalProps) {
  const buttonVariants = {
    default: 'bg-blue-600 hover:bg-blue-700 text-white',
    success: 'bg-green-600 hover:bg-green-700 text-white',
    warning: 'bg-yellow-600 hover:bg-yellow-700 text-white',
    error: 'bg-red-600 hover:bg-red-700 text-white'
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={title}
      variant={variant}
      size="sm"
    >
      <div className="space-y-4">
        <p className="text-gray-600 dark:text-gray-400">
          {message}
        </p>

        <ModalFooter justify="end">
          <button
            onClick={onClose}
            disabled={loading}
            className="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors disabled:opacity-50"
          >
            {cancelText}
          </button>
          <button
            onClick={onConfirm}
            disabled={loading}
            className={`
              px-4 py-2 rounded-lg font-medium transition-colors disabled:opacity-50
              ${buttonVariants[variant]}
              ${loading ? 'cursor-not-allowed' : ''}
            `}
          >
            {loading ? (
              <div className="flex items-center space-x-2">
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                <span>Loading...</span>
              </div>
            ) : (
              confirmText
            )}
          </button>
        </ModalFooter>
      </div>
    </Modal>
  );
}

export default Modal;
