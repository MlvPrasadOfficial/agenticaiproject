'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { ChevronRight, Home, MoreHorizontal } from 'lucide-react';

interface BreadcrumbItem {
  id: string;
  label: string;
  href?: string;
  onClick?: () => void;
  icon?: React.ReactNode;
  disabled?: boolean;
}

interface BreadcrumbsProps {
  items: BreadcrumbItem[];
  separator?: React.ReactNode;
  maxItems?: number;
  showHomeIcon?: boolean;
  className?: string;
  itemClassName?: string;
  separatorClassName?: string;
  collapsedItemsLabel?: string;
}

export function Breadcrumbs({
  items,
  separator,
  maxItems = 5,
  showHomeIcon = true,
  className = '',
  itemClassName = '',
  separatorClassName = '',
  collapsedItemsLabel = 'Show more'
}: BreadcrumbsProps) {
  const [showCollapsed, setShowCollapsed] = useState(false);

  // Handle truncation for long breadcrumb paths
  const getDisplayItems = () => {
    if (items.length <= maxItems) {
      return { items, hasCollapsed: false };
    }

    if (showCollapsed) {
      return { items, hasCollapsed: false };
    }

    // Show first item, collapsed indicator, and last 2 items
    const firstItem = items[0];
    const lastItems = items.slice(-2);
    const collapsedCount = items.length - 3;

    return {
      items: [
        firstItem,
        {
          id: 'collapsed',
          label: `${collapsedCount} more`,
          onClick: () => setShowCollapsed(true)
        },
        ...lastItems
      ],
      hasCollapsed: true
    };
  };

  const { items: displayItems, hasCollapsed } = getDisplayItems();

  const defaultSeparator = (
    <ChevronRight className="w-4 h-4 text-gray-400 dark:text-gray-500" />
  );

  const handleItemClick = (item: BreadcrumbItem, index: number) => {
    if (item.disabled) return;
    
    if (item.onClick) {
      item.onClick();
    } else if (item.href && typeof window !== 'undefined') {
      window.location.href = item.href;
    }
  };

  const renderBreadcrumbItem = (item: BreadcrumbItem, index: number, isLast: boolean) => {
    const isCollapsedItem = item.id === 'collapsed';
    const isClickable = (item.href || item.onClick) && !item.disabled;

    const itemContent = (
      <span className="flex items-center gap-1.5">
        {/* Home icon for first item */}
        {index === 0 && showHomeIcon && !item.icon && (
          <Home className="w-4 h-4" />
        )}
        
        {/* Custom icon */}
        {item.icon && (
          <span className="flex-shrink-0">
            {item.icon}
          </span>
        )}
        
        {/* Collapsed indicator */}
        {isCollapsedItem && (
          <MoreHorizontal className="w-4 h-4" />
        )}
        
        <span className="truncate max-w-[200px]">
          {item.label}
        </span>
      </span>
    );

    const baseClasses = `
      inline-flex items-center gap-1.5 px-2 py-1 rounded-md text-sm
      transition-all duration-200 ease-in-out
      ${item.disabled ? 'opacity-50 cursor-not-allowed' : ''}
      ${itemClassName}
    `;

    if (isLast) {
      // Last item (current page) - not clickable
      return (
        <span
          key={item.id}
          className={`
            ${baseClasses}
            text-gray-900 dark:text-gray-100 font-medium
            bg-gray-100 dark:bg-gray-800
          `}
        >
          {itemContent}
        </span>
      );
    }

    if (isClickable) {
      // Clickable breadcrumb item
      return (
        <motion.button
          key={item.id}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => handleItemClick(item, index)}
          className={`
            ${baseClasses}
            text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100
            hover:bg-gray-100 dark:hover:bg-gray-800
            focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
            dark:focus:ring-offset-gray-900
            ${isCollapsedItem ? 'italic' : ''}
          `}
        >
          {itemContent}
        </motion.button>
      );
    }

    // Non-clickable breadcrumb item
    return (
      <span
        key={item.id}
        className={`
          ${baseClasses}
          text-gray-500 dark:text-gray-400
        `}
      >
        {itemContent}
      </span>
    );
  };

  const renderSeparator = (index: number) => (
    <span
      key={`separator-${index}`}
      className={`flex items-center mx-1 ${separatorClassName}`}
      aria-hidden="true"
    >
      {separator || defaultSeparator}
    </span>
  );

  if (items.length === 0) {
    return null;
  }

  return (
    <nav
      aria-label="Breadcrumb"
      className={`flex items-center flex-wrap gap-1 ${className}`}
    >
      <ol className="flex items-center gap-1">
        {displayItems.map((item, index) => {
          const isLast = index === displayItems.length - 1;
          
          return (
            <React.Fragment key={item.id}>
              <li className="flex items-center">
                {renderBreadcrumbItem(item, index, isLast)}
              </li>
              
              {/* Separator */}
              {!isLast && (
                <li>
                  {renderSeparator(index)}
                </li>
              )}
            </React.Fragment>
          );
        })}
      </ol>
      
      {/* Collapse/Expand toggle for long paths */}
      {hasCollapsed && (
        <motion.button
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          onClick={() => setShowCollapsed(!showCollapsed)}
          className="ml-2 px-2 py-1 text-xs text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 rounded transition-colors duration-200"
        >
          {showCollapsed ? 'Show less' : collapsedItemsLabel}
        </motion.button>
      )}
    </nav>
  );
}

// Enhanced breadcrumb with animations and advanced features
interface AnimatedBreadcrumbsProps extends BreadcrumbsProps {
  animationDelay?: number;
  staggerChildren?: boolean;
}

export function AnimatedBreadcrumbs({
  animationDelay = 0,
  staggerChildren = true,
  ...props
}: AnimatedBreadcrumbsProps) {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        delay: animationDelay,
        staggerChildren: staggerChildren ? 0.1 : 0,
        delayChildren: 0.2
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, x: -20 },
    visible: {
      opacity: 1,
      x: 0,
      transition: {
        type: 'spring',
        stiffness: 100,
        damping: 12
      }
    }
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      <Breadcrumbs {...props} />
    </motion.div>
  );
}

// Hook for breadcrumb state management
export function useBreadcrumbs(initialItems: BreadcrumbItem[] = []) {
  const [items, setItems] = useState<BreadcrumbItem[]>(initialItems);

  const addItem = (item: BreadcrumbItem) => {
    setItems(prev => [...prev, item]);
  };

  const removeItem = (id: string) => {
    setItems(prev => prev.filter(item => item.id !== id));
  };

  const updateItem = (id: string, updates: Partial<BreadcrumbItem>) => {
    setItems(prev =>
      prev.map(item =>
        item.id === id ? { ...item, ...updates } : item
      )
    );
  };

  const setPath = (newItems: BreadcrumbItem[]) => {
    setItems(newItems);
  };

  const clear = () => {
    setItems([]);
  };

  const goToItem = (id: string) => {
    const itemIndex = items.findIndex(item => item.id === id);
    if (itemIndex !== -1) {
      setItems(prev => prev.slice(0, itemIndex + 1));
    }
  };

  return {
    items,
    addItem,
    removeItem,
    updateItem,
    setPath,
    clear,
    goToItem
  };
}

// Utility component for common breadcrumb patterns
interface PathBreadcrumbsProps {
  path: string;
  homeLabel?: string;
  onNavigate?: (path: string) => void;
  className?: string;
}

export function PathBreadcrumbs({
  path,
  homeLabel = 'Home',
  onNavigate,
  className
}: PathBreadcrumbsProps) {
  const pathSegments = path.split('/').filter(Boolean);
  
  const items: BreadcrumbItem[] = [
    {
      id: 'home',
      label: homeLabel,
      onClick: () => onNavigate?.('/')
    },
    ...pathSegments.map((segment, index) => {
      const segmentPath = '/' + pathSegments.slice(0, index + 1).join('/');
      return {
        id: segmentPath,
        label: segment.charAt(0).toUpperCase() + segment.slice(1).replace(/-/g, ' '),
        onClick: () => onNavigate?.(segmentPath)
      };
    })
  ];

  return <Breadcrumbs items={items} className={className} />;
}

// Example usage component
export function BreadcrumbsExample() {
  const exampleItems: BreadcrumbItem[] = [
    {
      id: 'home',
      label: 'Home',
      onClick: () => console.log('Navigate to home')
    },
    {
      id: 'products',
      label: 'Products',
      onClick: () => console.log('Navigate to products')
    },
    {
      id: 'category',
      label: 'Electronics',
      onClick: () => console.log('Navigate to electronics')
    },
    {
      id: 'subcategory',
      label: 'Laptops',
      onClick: () => console.log('Navigate to laptops')
    },
    {
      id: 'current',
      label: 'MacBook Pro 16"',
      // Current page - no onClick
    }
  ];

  return (
    <div className="space-y-6 p-6">
      <div>
        <h3 className="text-lg font-semibold mb-2">Standard Breadcrumbs</h3>
        <Breadcrumbs items={exampleItems} />
      </div>
      
      <div>
        <h3 className="text-lg font-semibold mb-2">Animated Breadcrumbs</h3>
        <AnimatedBreadcrumbs items={exampleItems} />
      </div>
      
      <div>
        <h3 className="text-lg font-semibold mb-2">Path Breadcrumbs</h3>
        <PathBreadcrumbs
          path="/products/electronics/laptops/macbook-pro"
          onNavigate={(path) => console.log('Navigate to:', path)}
        />
      </div>
      
      <div>
        <h3 className="text-lg font-semibold mb-2">Truncated Breadcrumbs</h3>
        <Breadcrumbs
          items={[
            ...exampleItems,
            { id: 'extra1', label: 'Extra Item 1' },
            { id: 'extra2', label: 'Extra Item 2' },
            { id: 'extra3', label: 'Extra Item 3' }
          ]}
          maxItems={4}
        />
      </div>
    </div>
  );
}
