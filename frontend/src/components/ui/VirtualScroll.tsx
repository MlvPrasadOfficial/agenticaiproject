'use client';

import React, { useState, useRef, useCallback, useMemo } from 'react';
import { useReducedMotion } from '@/lib/accessibility';

interface VirtualScrollProps<T> {
  readonly items: T[];
  readonly itemHeight: number;
  readonly containerHeight: number;
  readonly renderItem: (item: T, index: number) => React.ReactNode;
  readonly overscan?: number;
  readonly className?: string;
  readonly onScroll?: (scrollTop: number) => void;
  readonly 'aria-label'?: string;
}

export default function VirtualScroll<T>({
  items,
  itemHeight,
  containerHeight,
  renderItem,
  overscan = 3,
  className = '',
  onScroll,
  'aria-label': ariaLabel = 'Virtual scrollable list'
}: VirtualScrollProps<T>) {
  const [scrollTop, setScrollTop] = useState(0);
  const scrollElementRef = useRef<HTMLDivElement>(null);
  const prefersReducedMotion = useReducedMotion();

  const handleScroll = useCallback((e: React.UIEvent<HTMLDivElement>) => {
    const newScrollTop = e.currentTarget.scrollTop;
    setScrollTop(newScrollTop);
    onScroll?.(newScrollTop);
  }, [onScroll]);

  // Calculate visible range
  const visibleRange = useMemo(() => {
    const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan);
    const endIndex = Math.min(
      items.length - 1,
      Math.ceil((scrollTop + containerHeight) / itemHeight) + overscan
    );
    return { startIndex, endIndex };
  }, [scrollTop, itemHeight, containerHeight, overscan, items.length]);

  // Calculate total height and offset
  const totalHeight = items.length * itemHeight;
  const offsetY = visibleRange.startIndex * itemHeight;

  // Visible items
  const visibleItems = useMemo(() => {
    return items.slice(visibleRange.startIndex, visibleRange.endIndex + 1);
  }, [items, visibleRange]);

  // Keyboard navigation
  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (!scrollElementRef.current) return;

    const itemsPerPage = Math.floor(containerHeight / itemHeight);

    switch (e.key) {
      case 'ArrowUp':
        e.preventDefault();
        scrollElementRef.current.scrollTop = Math.max(0, scrollTop - itemHeight);
        break;
      case 'ArrowDown':
        e.preventDefault();
        scrollElementRef.current.scrollTop = Math.min(totalHeight - containerHeight, scrollTop + itemHeight);
        break;
      case 'PageUp':
        e.preventDefault();
        scrollElementRef.current.scrollTop = Math.max(0, scrollTop - itemsPerPage * itemHeight);
        break;
      case 'PageDown':
        e.preventDefault();
        scrollElementRef.current.scrollTop = Math.min(totalHeight - containerHeight, scrollTop + itemsPerPage * itemHeight);
        break;
      case 'Home':
        e.preventDefault();
        scrollElementRef.current.scrollTop = 0;
        break;
      case 'End':
        e.preventDefault();
        scrollElementRef.current.scrollTop = totalHeight - containerHeight;
        break;
    }
  }, [scrollTop, itemHeight, containerHeight, totalHeight]);

  return (
    <div
      ref={scrollElementRef}
      className={`overflow-auto ${className}`}
      style={{ height: containerHeight }}
      onScroll={prefersReducedMotion ? undefined : handleScroll}
      onKeyDown={handleKeyDown}
      tabIndex={0}
      role="grid"
      aria-label={ariaLabel}
      aria-rowcount={items.length}
    >
      <div
        style={{ height: totalHeight, position: 'relative' }}
        role="presentation"
      >
        <div
          style={{
            transform: `translateY(${offsetY}px)`,
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
          }}
        >
          {visibleItems.map((item, index) => (
            <div
              key={visibleRange.startIndex + index}
              style={{ height: itemHeight }}
              role="row"
              aria-rowindex={visibleRange.startIndex + index + 1}
            >
              {renderItem(item, visibleRange.startIndex + index)}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// Hook for managing virtual scroll state
export function useVirtualScroll<T>(items: T[], itemHeight: number, containerHeight: number) {
  const [scrollTop, setScrollTop] = useState(0);
  
  const visibleRange = useMemo(() => {
    const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - 3);
    const endIndex = Math.min(
      items.length - 1,
      Math.ceil((scrollTop + containerHeight) / itemHeight) + 3
    );
    return { startIndex, endIndex };
  }, [scrollTop, itemHeight, containerHeight, items.length]);

  const visibleItems = useMemo(() => {
    return items.slice(visibleRange.startIndex, visibleRange.endIndex + 1);
  }, [items, visibleRange]);

  const totalHeight = items.length * itemHeight;
  const offsetY = visibleRange.startIndex * itemHeight;

  return {
    scrollTop,
    setScrollTop,
    visibleRange,
    visibleItems,
    totalHeight,
    offsetY,
  };
}

// Virtual table component with accessibility features
interface VirtualTableProps<T> {
  data: T[];
  columns: Array<{
    key: keyof T;
    header: string;
    width?: number;
    render?: (value: T[keyof T], item: T, index: number) => React.ReactNode;
  }>;
  itemHeight?: number;
  containerHeight?: number;
  className?: string;
  onRowClick?: (item: T, index: number) => void;
  'aria-label'?: string;
}

export function VirtualTable<T extends Record<string, any>>({
  data,
  columns,
  itemHeight = 48,
  containerHeight = 400,
  className = '',
  onRowClick,
  'aria-label': ariaLabel = 'Data table'
}: VirtualTableProps<T>) {
  const renderRow = useCallback((item: T, index: number) => (
    <div
      className={`flex items-center border-b border-border hover:bg-surface/50 transition-colors ${
        onRowClick ? 'cursor-pointer' : ''
      }`}
      onClick={() => onRowClick?.(item, index)}
      role="row"
      tabIndex={onRowClick ? 0 : undefined}
      onKeyDown={onRowClick ? (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onRowClick(item, index);
        }
      } : undefined}
    >
      {columns.map((column, colIndex) => (
        <div
          key={String(column.key)}
          className="px-4 py-2 text-sm text-text-secondary"
          style={{ width: column.width || `${100 / columns.length}%` }}
          role="cell"
          aria-describedby={`column-${colIndex}`}
        >
          {column.render
            ? column.render(item[column.key], item, index)
            : String(item[column.key] || '')}
        </div>
      ))}
    </div>
  ), [columns, onRowClick]);

  return (
    <div className={`border border-border rounded-lg overflow-hidden ${className}`}>
      {/* Table header */}
      <div className="flex bg-surface border-b border-border" role="row">
        {columns.map((column, index) => (
          <div
            key={String(column.key)}
            id={`column-${index}`}
            className="px-4 py-3 text-sm font-semibold text-text-primary"
            style={{ width: column.width || `${100 / columns.length}%` }}
            role="columnheader"
          >
            {column.header}
          </div>
        ))}
      </div>

      {/* Virtual scrolled content */}
      <VirtualScroll
        items={data}
        itemHeight={itemHeight}
        containerHeight={containerHeight}
        renderItem={renderRow}
        aria-label={ariaLabel}
        className="bg-background"
      />
    </div>
  );
}
