'use client';

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  ChevronUp, 
  ChevronDown, 
  MoreHorizontal, 
  Filter,
  ArrowUpDown,
  Search,
  Download,
  Settings,
  Eye,
  EyeOff,
  Maximize2,
  Minimize2
} from 'lucide-react';

interface ColumnConfig {
  key: string;
  label: string;
  type?: 'string' | 'number' | 'date' | 'boolean' | 'custom';
  sortable?: boolean;
  filterable?: boolean;
  resizable?: boolean;
  width?: number;
  minWidth?: number;
  maxWidth?: number;
  visible?: boolean;
  formatter?: (value: any, row: any) => React.ReactNode;
  align?: 'left' | 'center' | 'right';
}

interface TableRow {
  id: string | number;
  [key: string]: any;
}

interface DataTableSmartProps {
  data: TableRow[];
  columns: ColumnConfig[];
  title?: string;
  searchable?: boolean;
  exportable?: boolean;
  selectable?: boolean;
  pageSize?: number;
  virtualScrolling?: boolean;
  height?: number;
  onRowClick?: (row: TableRow) => void;
  onRowSelect?: (selectedRows: TableRow[]) => void;
  onExport?: (format: 'csv' | 'xlsx' | 'json') => void;
  className?: string;
}

export function DataTableSmart({
  data,
  columns: initialColumns,
  title,
  searchable = true,
  exportable = true,
  selectable = false,
  pageSize = 50,
  virtualScrolling = false,
  height = 600,
  onRowClick,
  onRowSelect,
  onExport,
  className = ''
}: DataTableSmartProps) {
  const [columns, setColumns] = useState<ColumnConfig[]>(initialColumns);
  const [sortConfig, setSortConfig] = useState<{ key: string; direction: 'asc' | 'desc' } | null>(null);
  const [filters, setFilters] = useState<Record<string, string>>({});
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedRows, setSelectedRows] = useState<Set<string | number>>(new Set());
  const [columnWidths, setColumnWidths] = useState<Record<string, number>>({});
  const [isResizing, setIsResizing] = useState<string | null>(null);
  const [showColumnSettings, setShowColumnSettings] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  
  const tableRef = useRef<HTMLDivElement>(null);
  const resizeRef = useRef<{ startX: number; startWidth: number; column: string } | null>(null);

  // Initialize column widths
  useEffect(() => {
    const widths: Record<string, number> = {};
    columns.forEach(col => {
      if (col.width) {
        widths[col.key] = col.width;
      } else {
        widths[col.key] = 150; // default width
      }
    });
    setColumnWidths(widths);
  }, [columns]);

  // Filter and sort data
  const processedData = React.useMemo(() => {
    let filtered = data;

    // Apply search filter
    if (searchTerm) {
      filtered = filtered.filter(row =>
        Object.values(row).some(value =>
          String(value).toLowerCase().includes(searchTerm.toLowerCase())
        )
      );
    }

    // Apply column filters
    Object.entries(filters).forEach(([key, value]) => {
      if (value) {
        filtered = filtered.filter(row =>
          String(row[key]).toLowerCase().includes(value.toLowerCase())
        );
      }
    });

    // Apply sorting
    if (sortConfig) {
      filtered.sort((a, b) => {
        const aVal = a[sortConfig.key];
        const bVal = b[sortConfig.key];
        
        if (aVal < bVal) return sortConfig.direction === 'asc' ? -1 : 1;
        if (aVal > bVal) return sortConfig.direction === 'asc' ? 1 : -1;
        return 0;
      });
    }

    return filtered;
  }, [data, searchTerm, filters, sortConfig]);

  // Pagination
  const paginatedData = React.useMemo(() => {
    if (virtualScrolling) return processedData;
    
    const start = (currentPage - 1) * pageSize;
    return processedData.slice(start, start + pageSize);
  }, [processedData, currentPage, pageSize, virtualScrolling]);

  const totalPages = Math.ceil(processedData.length / pageSize);

  // Handle sorting
  const handleSort = (columnKey: string) => {
    setSortConfig(prev => {
      if (prev?.key === columnKey) {
        return prev.direction === 'asc' 
          ? { key: columnKey, direction: 'desc' }
          : null;
      }
      return { key: columnKey, direction: 'asc' };
    });
  };

  // Handle column resizing
  const handleMouseDown = useCallback((e: React.MouseEvent, columnKey: string) => {
    e.preventDefault();
    setIsResizing(columnKey);
    resizeRef.current = {
      startX: e.clientX,
      startWidth: columnWidths[columnKey],
      column: columnKey
    };
  }, [columnWidths]);

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (!isResizing || !resizeRef.current) return;

    const diff = e.clientX - resizeRef.current.startX;
    const newWidth = Math.max(60, resizeRef.current.startWidth + diff);
    
    setColumnWidths(prev => ({
      ...prev,
      [resizeRef.current!.column]: newWidth
    }));
  }, [isResizing]);

  const handleMouseUp = useCallback(() => {
    setIsResizing(null);
    resizeRef.current = null;
  }, []);

  useEffect(() => {
    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [isResizing, handleMouseMove, handleMouseUp]);

  // Handle row selection
  const handleRowSelect = (rowId: string | number) => {
    const newSelection = new Set(selectedRows);
    if (newSelection.has(rowId)) {
      newSelection.delete(rowId);
    } else {
      newSelection.add(rowId);
    }
    setSelectedRows(newSelection);
    onRowSelect?.(data.filter(row => newSelection.has(row.id)));
  };

  const handleSelectAll = () => {
    if (selectedRows.size === processedData.length) {
      setSelectedRows(new Set());
      onRowSelect?.([]);
    } else {
      const allIds = new Set(processedData.map(row => row.id));
      setSelectedRows(allIds);
      onRowSelect?.(processedData);
    }
  };

  // Toggle column visibility
  const toggleColumnVisibility = (columnKey: string) => {
    setColumns(prev => prev.map(col => 
      col.key === columnKey ? { ...col, visible: !col.visible } : col
    ));
  };

  const visibleColumns = columns.filter(col => col.visible !== false);

  return (
    <div className={`bg-white dark:bg-gray-900 rounded-xl shadow-lg overflow-hidden ${className}`}>
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div>
            {title && (
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                {title}
              </h3>
            )}
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              {processedData.length} rows • {visibleColumns.length} columns
            </p>
          </div>
          
          <div className="flex items-center gap-2">
            {searchable && (
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
                />
              </div>
            )}
            
            <button
              onClick={() => setShowColumnSettings(!showColumnSettings)}
              className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
            >
              <Settings className="w-4 h-4" />
            </button>
            
            {exportable && (
              <button
                onClick={() => onExport?.('csv')}
                className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
              >
                <Download className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>

        {/* Column Settings Panel */}
        <AnimatePresence>
          {showColumnSettings && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mt-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg"
            >
              <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
                Column Visibility
              </h4>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
                {columns.map(column => (
                  <label key={column.key} className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={column.visible !== false}
                      onChange={() => toggleColumnVisibility(column.key)}
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="text-sm text-gray-700 dark:text-gray-300">
                      {column.label}
                    </span>
                  </label>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Table */}
      <div 
        ref={tableRef}
        className="overflow-auto"
        style={{ height: virtualScrolling ? height : 'auto' }}
      >
        <table className="w-full">
          <thead className="bg-gray-50 dark:bg-gray-800 sticky top-0">
            <tr>
              {selectable && (
                <th className="w-12 px-4 py-3 text-left">
                  <input
                    type="checkbox"
                    checked={selectedRows.size === processedData.length && processedData.length > 0}
                    onChange={handleSelectAll}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                </th>
              )}
              {visibleColumns.map(column => (
                <th
                  key={column.key}
                  className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider relative group"
                  style={{ 
                    width: columnWidths[column.key],
                    minWidth: column.minWidth || 60,
                    maxWidth: column.maxWidth || 500
                  }}
                >
                  <div className="flex items-center justify-between">
                    <div 
                      className={`flex items-center space-x-1 ${
                        column.sortable !== false ? 'cursor-pointer hover:text-gray-700 dark:hover:text-gray-300' : ''
                      }`}
                      onClick={() => column.sortable !== false && handleSort(column.key)}
                    >
                      <span>{column.label}</span>
                      {column.sortable !== false && (
                        <div className="flex flex-col">
                          <ChevronUp 
                            className={`w-3 h-3 ${
                              sortConfig?.key === column.key && sortConfig.direction === 'asc'
                                ? 'text-blue-600 dark:text-blue-400'
                                : 'text-gray-300 dark:text-gray-600'
                            }`}
                          />
                          <ChevronDown 
                            className={`w-3 h-3 -mt-1 ${
                              sortConfig?.key === column.key && sortConfig.direction === 'desc'
                                ? 'text-blue-600 dark:text-blue-400'
                                : 'text-gray-300 dark:text-gray-600'
                            }`}
                          />
                        </div>
                      )}
                    </div>
                    
                    {/* Column Filter */}
                    {column.filterable !== false && (
                      <input
                        type="text"
                        placeholder="Filter..."
                        value={filters[column.key] || ''}
                        onChange={(e) => setFilters(prev => ({ ...prev, [column.key]: e.target.value }))}
                        className="ml-2 px-2 py-1 text-xs border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        onClick={(e) => e.stopPropagation()}
                      />
                    )}
                  </div>

                  {/* Resize Handle */}
                  {column.resizable !== false && (
                    <div
                      className="absolute right-0 top-0 h-full w-1 cursor-col-resize hover:bg-blue-500 opacity-0 group-hover:opacity-100 transition-opacity"
                      onMouseDown={(e) => handleMouseDown(e, column.key)}
                    />
                  )}
                </th>
              ))}
            </tr>
          </thead>
          
          <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
            {paginatedData.map((row, index) => (
              <motion.tr
                key={row.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.02 }}
                className={`hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors ${
                  selectedRows.has(row.id) ? 'bg-blue-50 dark:bg-blue-900/20' : ''
                } ${onRowClick ? 'cursor-pointer' : ''}`}
                onClick={() => onRowClick?.(row)}
              >
                {selectable && (
                  <td className="px-4 py-3">
                    <input
                      type="checkbox"
                      checked={selectedRows.has(row.id)}
                      onChange={(e) => {
                        e.stopPropagation();
                        handleRowSelect(row.id);
                      }}
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                  </td>
                )}
                {visibleColumns.map(column => (
                  <td
                    key={column.key}
                    className={`px-4 py-3 text-sm text-gray-900 dark:text-white ${
                      column.align === 'center' ? 'text-center' : 
                      column.align === 'right' ? 'text-right' : 'text-left'
                    }`}
                    style={{ width: columnWidths[column.key] }}
                  >
                    {column.formatter 
                      ? column.formatter(row[column.key], row)
                      : String(row[column.key] || '')
                    }
                  </td>
                ))}
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {!virtualScrolling && totalPages > 1 && (
        <div className="px-6 py-4 border-t border-gray-200 dark:border-gray-700 flex items-center justify-between">
          <div className="text-sm text-gray-500 dark:text-gray-400">
            Showing {(currentPage - 1) * pageSize + 1} to {Math.min(currentPage * pageSize, processedData.length)} of {processedData.length} results
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
              disabled={currentPage === 1}
              className="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 dark:hover:bg-gray-800"
            >
              Previous
            </button>
            
            <span className="text-sm text-gray-700 dark:text-gray-300">
              Page {currentPage} of {totalPages}
            </span>
            
            <button
              onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
              disabled={currentPage === totalPages}
              className="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 dark:hover:bg-gray-800"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
