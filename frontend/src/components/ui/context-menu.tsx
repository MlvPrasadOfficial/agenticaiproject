'use client';

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { createPortal } from 'react-dom';

interface MenuItem {
  id: string;
  label: string;
  icon?: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  divider?: boolean;
  submenu?: MenuItem[];
  shortcut?: string;
  danger?: boolean;
}

interface ContextMenuProps {
  items: MenuItem[];
  children: React.ReactNode;
  disabled?: boolean;
  className?: string;
  onOpenChange?: (open: boolean) => void;
}

export function ContextMenu({
  items,
  children,
  disabled = false,
  className = '',
  onOpenChange
}: ContextMenuProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [submenuStates, setSubmenuStates] = useState<Record<string, boolean>>({});
  const triggerRef = useRef<HTMLDivElement>(null);
  const menuRef = useRef<HTMLDivElement>(null);

  const openMenu = useCallback((event: React.MouseEvent) => {
    if (disabled) return;
    
    event.preventDefault();
    event.stopPropagation();

    const rect = event.currentTarget.getBoundingClientRect();
    const x = event.clientX;
    const y = event.clientY;

    setPosition({ x, y });
    setIsOpen(true);
    onOpenChange?.(true);
  }, [disabled, onOpenChange]);

  const closeMenu = useCallback(() => {
    setIsOpen(false);
    setSubmenuStates({});
    onOpenChange?.(false);
  }, [onOpenChange]);

  const handleItemClick = useCallback((item: MenuItem) => {
    if (item.disabled || item.submenu) return;
    
    item.onClick?.();
    closeMenu();
  }, [closeMenu]);

  const toggleSubmenu = useCallback((itemId: string) => {
    setSubmenuStates(prev => ({
      ...prev,
      [itemId]: !prev[itemId]
    }));
  }, []);

  // Close menu on outside click
  useEffect(() => {
    if (!isOpen) return;

    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        closeMenu();
      }
    };

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        closeMenu();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleEscape);

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleEscape);
    };
  }, [isOpen, closeMenu]);

  // Adjust position to prevent menu from going off-screen
  const adjustPosition = useCallback(() => {
    if (!menuRef.current) return;

    const menu = menuRef.current;
    const rect = menu.getBoundingClientRect();
    const viewport = {
      width: window.innerWidth,
      height: window.innerHeight
    };

    let { x, y } = position;

    // Adjust horizontal position
    if (x + rect.width > viewport.width - 10) {
      x = viewport.width - rect.width - 10;
    }
    if (x < 10) {
      x = 10;
    }

    // Adjust vertical position
    if (y + rect.height > viewport.height - 10) {
      y = viewport.height - rect.height - 10;
    }
    if (y < 10) {
      y = 10;
    }

    if (x !== position.x || y !== position.y) {
      setPosition({ x, y });
    }
  }, [position]);

  useEffect(() => {
    if (isOpen) {
      // Adjust position after menu is rendered
      setTimeout(adjustPosition, 0);
    }
  }, [isOpen, adjustPosition]);

  const menuVariants = {
    hidden: {
      opacity: 0,
      scale: 0.95,
      y: -10
    },
    visible: {
      opacity: 1,
      scale: 1,
      y: 0,
      transition: {
        duration: 0.15,
        ease: 'easeOut'
      }
    },
    exit: {
      opacity: 0,
      scale: 0.95,
      y: -10,
      transition: {
        duration: 0.1,
        ease: 'easeIn'
      }
    }
  };

  const renderMenuItem = (item: MenuItem, depth = 0) => {
    if (item.divider) {
      return (
        <div key={item.id} className="my-1">
          <div className="h-px bg-gray-200 dark:bg-gray-700 mx-2" />
        </div>
      );
    }

    const hasSubmenu = item.submenu && item.submenu.length > 0;
    const isSubmenuOpen = submenuStates[item.id];

    return (
      <div key={item.id} className="relative">
        <button
          className={`
            w-full px-3 py-2 text-left text-sm flex items-center gap-3
            transition-colors duration-150 hover:bg-gray-100 dark:hover:bg-gray-700
            ${item.disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
            ${item.danger ? 'text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20' : 'text-gray-700 dark:text-gray-300'}
          `}
          disabled={item.disabled}
          onClick={() => {
            if (hasSubmenu) {
              toggleSubmenu(item.id);
            } else {
              handleItemClick(item);
            }
          }}
          onMouseEnter={() => {
            if (hasSubmenu && !isSubmenuOpen) {
              setTimeout(() => toggleSubmenu(item.id), 300);
            }
          }}
        >
          {item.icon && (
            <span className="flex-shrink-0 w-4 h-4">
              {item.icon}
            </span>
          )}
          
          <span className="flex-1 truncate">
            {item.label}
          </span>
          
          {item.shortcut && (
            <span className="text-xs text-gray-400 dark:text-gray-500 ml-auto">
              {item.shortcut}
            </span>
          )}
          
          {hasSubmenu && (
            <span className="ml-auto">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </span>
          )}
        </button>
        
        {/* Submenu */}
        <AnimatePresence>
          {hasSubmenu && isSubmenuOpen && (
            <motion.div
              initial="hidden"
              animate="visible"
              exit="exit"
              variants={menuVariants}
              className={`
                absolute left-full top-0 ml-1 min-w-[200px]
                bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700
                backdrop-blur-sm z-10
              `}
            >
              <div className="py-1">
                {item.submenu!.map(subItem => renderMenuItem(subItem, depth + 1))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    );
  };

  const menu = (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          ref={menuRef}
          initial="hidden"
          animate="visible"
          exit="exit"
          variants={menuVariants}
          className={`
            fixed z-[9999] min-w-[200px] max-w-[300px]
            bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700
            backdrop-blur-sm
            ${className}
          `}
          style={{
            left: position.x,
            top: position.y
          }}
        >
          <div className="py-1">
            {items.map(item => renderMenuItem(item))}
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );

  return (
    <>
      <div
        ref={triggerRef}
        onContextMenu={openMenu}
        className="cursor-context-menu"
      >
        {children}
      </div>
      {typeof window !== 'undefined' && createPortal(menu, document.body)}
    </>
  );
}

// Hook for programmatic context menu
export function useContextMenu() {
  const [isOpen, setIsOpen] = useState(false);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [items, setItems] = useState<MenuItem[]>([]);

  const showContextMenu = useCallback((event: MouseEvent | React.MouseEvent, menuItems: MenuItem[]) => {
    event.preventDefault();
    event.stopPropagation();

    setItems(menuItems);
    setPosition({ x: event.clientX, y: event.clientY });
    setIsOpen(true);
  }, []);

  const hideContextMenu = useCallback(() => {
    setIsOpen(false);
  }, []);

  const ContextMenuComponent = useCallback(() => (
    <ContextMenu items={items} disabled={!isOpen}>
      <div />
    </ContextMenu>
  ), [items, isOpen]);

  return {
    showContextMenu,
    hideContextMenu,
    isOpen,
    ContextMenuComponent
  };
}

// Utility component for quick context menu setup
interface QuickContextMenuProps {
  items: MenuItem[];
  children: React.ReactNode;
  disabled?: boolean;
}

export function QuickContextMenu({ items, children, disabled }: QuickContextMenuProps) {
  return (
    <ContextMenu items={items} disabled={disabled}>
      {children}
    </ContextMenu>
  );
}

// Example usage component
export function ContextMenuExample() {
  const menuItems: MenuItem[] = [
    {
      id: 'copy',
      label: 'Copy',
      icon: (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
        </svg>
      ),
      shortcut: 'Ctrl+C',
      onClick: () => console.log('Copy clicked')
    },
    {
      id: 'paste',
      label: 'Paste',
      icon: (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
        </svg>
      ),
      shortcut: 'Ctrl+V',
      onClick: () => console.log('Paste clicked'),
      disabled: true
    },
    { id: 'divider1', label: '', divider: true },
    {
      id: 'share',
      label: 'Share',
      icon: (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
        </svg>
      ),
      submenu: [
        {
          id: 'email',
          label: 'Send via Email',
          onClick: () => console.log('Email share clicked')
        },
        {
          id: 'link',
          label: 'Copy Link',
          onClick: () => console.log('Copy link clicked')
        },
        {
          id: 'social',
          label: 'Social Media',
          submenu: [
            {
              id: 'twitter',
              label: 'Twitter',
              onClick: () => console.log('Twitter share clicked')
            },
            {
              id: 'facebook',
              label: 'Facebook',
              onClick: () => console.log('Facebook share clicked')
            }
          ]
        }
      ]
    },
    { id: 'divider2', label: '', divider: true },
    {
      id: 'delete',
      label: 'Delete',
      icon: (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
        </svg>
      ),
      shortcut: 'Del',
      danger: true,
      onClick: () => console.log('Delete clicked')
    }
  ];

  return (
    <ContextMenu items={menuItems}>
      <div className="w-64 h-32 bg-gray-100 dark:bg-gray-800 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg flex items-center justify-center">
        <p className="text-gray-500 dark:text-gray-400">Right-click me!</p>
      </div>
    </ContextMenu>
  );
}
