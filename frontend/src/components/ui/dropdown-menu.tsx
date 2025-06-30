'use client';

import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, Check } from 'lucide-react';

interface DropdownItem {
  id: string;
  label: string;
  value?: any;
  icon?: React.ReactNode;
  disabled?: boolean;
  divider?: boolean;
}

interface DropdownMenuProps {
  trigger: React.ReactNode;
  items: DropdownItem[];
  selectedValue?: any;
  onSelect?: (item: DropdownItem) => void;
  placeholder?: string;
  className?: string;
  menuClassName?: string;
  position?: 'bottom-left' | 'bottom-right' | 'top-left' | 'top-right';
  width?: 'auto' | 'trigger' | string;
  maxHeight?: string;
  searchable?: boolean;
  multiSelect?: boolean;
  disabled?: boolean;
}

export function DropdownMenu({
  trigger,
  items,
  selectedValue,
  onSelect,
  placeholder = 'Select an option',
  className = '',
  menuClassName = '',
  position = 'bottom-left',
  width = 'auto',
  maxHeight = '300px',
  searchable = false,
  multiSelect = false,
  disabled = false
}: DropdownMenuProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedItems, setSelectedItems] = useState<any[]>(
    multiSelect ? (Array.isArray(selectedValue) ? selectedValue : []) : []
  );
  
  const dropdownRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLButtonElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
        setSearchQuery('');
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Filter items based on search query
  const filteredItems = searchable 
    ? items.filter(item => 
        item.label.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : items;

  const handleItemSelect = (item: DropdownItem) => {
    if (item.disabled) return;

    if (multiSelect) {
      const newSelectedItems = selectedItems.includes(item.value)
        ? selectedItems.filter(val => val !== item.value)
        : [...selectedItems, item.value];
      
      setSelectedItems(newSelectedItems);
      onSelect?.({ ...item, value: newSelectedItems });
    } else {
      setIsOpen(false);
      setSearchQuery('');
      onSelect?.(item);
    }
  };

  const isSelected = (item: DropdownItem) => {
    if (multiSelect) {
      return selectedItems.includes(item.value);
    }
    return selectedValue === item.value;
  };

  const positionClasses = {
    'bottom-left': 'top-full left-0 mt-2',
    'bottom-right': 'top-full right-0 mt-2',
    'top-left': 'bottom-full left-0 mb-2',
    'top-right': 'bottom-full right-0 mb-2'
  };

  const getMenuWidth = () => {
    if (width === 'trigger' && triggerRef.current) {
      return `${triggerRef.current.offsetWidth}px`;
    }
    return width === 'auto' ? 'auto' : width;
  };

  return (
    <div className={`relative inline-block ${className}`} ref={dropdownRef}>
      {/* Trigger */}
      <button
        ref={triggerRef}
        onClick={() => !disabled && setIsOpen(!isOpen)}
        disabled={disabled}
        className={`
          ${trigger ? '' : 'flex items-center justify-between w-full px-4 py-2'}
          ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
          ${!trigger ? 'bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg hover:border-gray-400 dark:hover:border-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500/30 transition-colors' : ''}
        `}
        aria-haspopup="listbox"
        aria-expanded={isOpen}
      >
        {trigger || (
          <>
            <span className="text-gray-900 dark:text-gray-100">
              {multiSelect
                ? selectedItems.length > 0 
                  ? `${selectedItems.length} selected`
                  : placeholder
                : selectedValue
                  ? items.find(item => item.value === selectedValue)?.label
                  : placeholder
              }
            </span>
            <ChevronDown 
              className={`w-4 h-4 text-gray-500 transition-transform duration-200 ${
                isOpen ? 'rotate-180' : ''
              }`} 
            />
          </>
        )}
      </button>

      {/* Dropdown Menu */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.95 }}
            transition={{ duration: 0.15, ease: "easeOut" }}
            className={`
              absolute z-50 ${positionClasses[position]}
              bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700
              rounded-xl shadow-xl backdrop-blur-sm
              ${menuClassName}
            `}
            style={{ 
              width: getMenuWidth(),
              maxHeight: maxHeight,
              overflow: 'hidden'
            }}
            role="listbox"
          >
            {/* Search Input */}
            {searchable && (
              <div className="p-3 border-b border-gray-200 dark:border-gray-700">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search..."
                  className="w-full px-3 py-2 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/30"
                  autoFocus
                />
              </div>
            )}

            {/* Menu Items */}
            <div className="max-h-60 overflow-y-auto py-1">
              {filteredItems.length === 0 ? (
                <div className="px-4 py-3 text-sm text-gray-500 dark:text-gray-400 text-center">
                  No options found
                </div>
              ) : (
                filteredItems.map((item, index) => {
                  if (item.divider) {
                    return (
                      <hr 
                        key={`divider-${index}`} 
                        className="my-1 border-gray-200 dark:border-gray-700" 
                      />
                    );
                  }

                  const selected = isSelected(item);

                  return (
                    <motion.button
                      key={item.id}
                      whileHover={{ backgroundColor: 'var(--hover-bg)' }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => handleItemSelect(item)}
                      disabled={item.disabled}
                      className={`
                        w-full flex items-center justify-between px-4 py-2.5 text-left
                        transition-colors duration-150
                        ${item.disabled 
                          ? 'text-gray-400 dark:text-gray-500 cursor-not-allowed' 
                          : 'text-gray-900 dark:text-gray-100 hover:bg-gray-50 dark:hover:bg-gray-700'
                        }
                        ${selected ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400' : ''}
                      `}
                      style={{ '--hover-bg': selected ? undefined : 'rgb(249 250 251 / 1)' } as any}
                      role="option"
                      aria-selected={selected}
                    >
                      <div className="flex items-center space-x-3">
                        {item.icon && (
                          <span className="flex-shrink-0">
                            {item.icon}
                          </span>
                        )}
                        <span className="font-medium">{item.label}</span>
                      </div>
                      
                      {selected && (
                        <Check className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                      )}
                    </motion.button>
                  );
                })
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default DropdownMenu;
