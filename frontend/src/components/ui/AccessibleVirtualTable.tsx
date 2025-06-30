'use client';

import React, { useState, useCallback, useMemo } from 'react';
import { useReducedMotion } from '@/lib/accessibility';

interface VirtualTableProps<T> {
  readonly data: T[];
  readonly columns: ReadonlyArray<{
    readonly key: keyof T;
    readonly header: string;
    readonly width?: number;
    readonly render?: (value: T[keyof T], item: T, index: number) => React.ReactNode;
  }>;
  readonly itemHeight?: number;
  readonly containerHeight?: number;
  readonly className?: string;
  readonly onRowClick?: (item: T, index: number) => void;
  readonly 'aria-label'?: string;
}

export function AccessibleVirtualTable<T extends Record<string, any>>({
  data,
  columns,
  itemHeight = 48,
  containerHeight = 400,
  className = '',
  onRowClick,
  'aria-label': ariaLabel = 'Data table'
}: VirtualTableProps<T>) {
  const [scrollTop, setScrollTop] = useState(0);
  const prefersReducedMotion = useReducedMotion();

  const handleScroll = useCallback((e: React.UIEvent<HTMLDivElement>) => {
    if (!prefersReducedMotion) {
      setScrollTop(e.currentTarget.scrollTop);
    }
  }, [prefersReducedMotion]);

  // Calculate visible range with overscan
  const visibleRange = useMemo(() => {
    const overscan = 3;
    const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan);
    const endIndex = Math.min(
      data.length - 1,
      Math.ceil((scrollTop + containerHeight) / itemHeight) + overscan
    );
    return { startIndex, endIndex };
  }, [scrollTop, itemHeight, containerHeight, data.length]);

  const visibleItems = useMemo(() => {
    return data.slice(visibleRange.startIndex, visibleRange.endIndex + 1);
  }, [data, visibleRange]);

  const totalHeight = data.length * itemHeight;
  const offsetY = visibleRange.startIndex * itemHeight;

  return (
    <div className={`border border-border rounded-lg overflow-hidden ${className}`}>
      <table className="w-full" aria-label={ariaLabel}>
        <thead className="bg-surface border-b border-border sticky top-0 z-10">
          <tr>
            {columns.map((column, index) => (
              <th
                key={String(column.key)}
                scope="col"
                className="px-4 py-3 text-left text-sm font-semibold text-text-primary"
                style={{ width: column.width ?? `${100 / columns.length}%` }}
              >
                {column.header}
              </th>
            ))}
          </tr>
        </thead>
      </table>

      <div
        className="overflow-auto bg-background"
        style={{ height: containerHeight }}
        onScroll={handleScroll}
        tabIndex={0}
        role="region"
        aria-label="Scrollable table content"
      >
        <div style={{ height: totalHeight, position: 'relative' }}>
          <div
            style={{
              transform: `translateY(${offsetY}px)`,
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
            }}
          >
            <table className="w-full">
              <tbody>
                {visibleItems.map((item, index) => {
                  const actualIndex = visibleRange.startIndex + index;
                  return (
                    <tr
                      key={actualIndex}
                      className={`border-b border-border hover:bg-surface/50 transition-colors ${
                        onRowClick ? 'cursor-pointer focus:bg-surface focus:outline-none' : ''
                      }`}
                      style={{ height: itemHeight }}
                      onClick={() => onRowClick?.(item, actualIndex)}
                      tabIndex={onRowClick ? 0 : undefined}
                      onKeyDown={onRowClick ? (e) => {
                        if (e.key === 'Enter' || e.key === ' ') {
                          e.preventDefault();
                          onRowClick(item, actualIndex);
                        }
                      } : undefined}
                      aria-rowindex={actualIndex + 1}
                    >
                      {columns.map((column) => (
                        <td
                          key={String(column.key)}
                          className="px-4 py-2 text-sm text-text-secondary"
                          style={{ width: column.width ?? `${100 / columns.length}%` }}
                        >
                          {column.render
                            ? column.render(item[column.key], item, actualIndex)
                            : String(item[column.key] ?? '')}
                        </td>
                      ))}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

// Performance monitoring hook
export function usePerformanceMonitor(componentName: string) {
  React.useEffect(() => {
    const startTime = performance.now();
    
    return () => {
      const endTime = performance.now();
      const renderTime = endTime - startTime;
      
      if (process.env.NODE_ENV === 'development' && renderTime > 100) {
        console.warn(`${componentName} render took ${renderTime.toFixed(2)}ms`);
      }
    };
  });
}

export default AccessibleVirtualTable;
