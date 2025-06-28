'use client';

import React, { useState, useMemo, useCallback } from 'react';
import { 
  ChevronUp, 
  ChevronDown, 
  Search, 
  Filter, 
  Download, 
  MoreHorizontal,
  Eye,
  EyeOff,
  ArrowUpDown
} from 'lucide-react';

export interface DataColumn {
  key: string;
  label: string;
  type: 'string' | 'number' | 'date' | 'boolean';
  sortable?: boolean;
  filterable?: boolean;
  visible?: boolean;
  width?: number;
  format?: (value: any) => string;
}

export interface DataTableProps {
  data: Record<string, any>[];
  columns: DataColumn[];
  title?: string;
  searchable?: boolean;
  exportable?: boolean;
  selectable?: boolean;
  pagination?: boolean;
  pageSize?: number;
  virtualScrolling?: boolean;
  height?: number;
  onRowSelect?: (selectedRows: Record<string, any>[]) => void;
  onExport?: (data: Record<string, any>[]) => void;
  className?: string;
}

const DataTable: React.FC<DataTableProps> = ({
  data,
  columns: initialColumns,
  title = 'Data Table',
  searchable = true,
  exportable = true,
  selectable = false,
  pagination = true,
  pageSize = 50,
  virtualScrolling = false,
  height = 400,
  onRowSelect,
  onExport,
  className = ''
}) => {
  const [columns, setColumns] = useState(initialColumns.map(col => ({ ...col, visible: col.visible ?? true })));
  const [sortConfig, setSortConfig] = useState<{ key: string; direction: 'asc' | 'desc' } | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState<Record<string, string>>({});
  const [selectedRows, setSelectedRows] = useState<Set<number>>(new Set());
  const [currentPage, setCurrentPage] = useState(1);
  const [showColumnSettings, setShowColumnSettings] = useState(false);

  // Filter and search data
  const filteredData = useMemo(() => {
    let result = [...data];

    // Apply search
    if (searchTerm) {
      result = result.filter(row =>
        Object.values(row).some(value =>
          String(value).toLowerCase().includes(searchTerm.toLowerCase())
        )
      );
    }

    // Apply column filters
    Object.entries(filters).forEach(([columnKey, filterValue]) => {
      if (filterValue) {
        result = result.filter(row =>
          String(row[columnKey]).toLowerCase().includes(filterValue.toLowerCase())
        );
      }
    });

    return result;
  }, [data, searchTerm, filters]);

  // Sort data
  const sortedData = useMemo(() => {
    if (!sortConfig) return filteredData;

    return [...filteredData].sort((a, b) => {
      const aValue = a[sortConfig.key];
      const bValue = b[sortConfig.key];

      if (aValue < bValue) {
        return sortConfig.direction === 'asc' ? -1 : 1;
      }
      if (aValue > bValue) {
        return sortConfig.direction === 'asc' ? 1 : -1;
      }
      return 0;
    });
  }, [filteredData, sortConfig]);

  // Paginate data
  const paginatedData = useMemo(() => {
    if (!pagination) return sortedData;

    const startIndex = (currentPage - 1) * pageSize;
    return sortedData.slice(startIndex, startIndex + pageSize);
  }, [sortedData, currentPage, pageSize, pagination]);

  const totalPages = Math.ceil(filteredData.length / pageSize);
  const visibleColumns = columns.filter(col => col.visible);

  const handleSort = useCallback((columnKey: string) => {
    setSortConfig(current => {
      if (current?.key === columnKey) {
        return current.direction === 'asc'
          ? { key: columnKey, direction: 'desc' }
          : null;
      }
      return { key: columnKey, direction: 'asc' };
    });
  }, []);

  const handleRowSelect = useCallback((rowIndex: number, isSelected: boolean) => {
    setSelectedRows(prev => {
      const newSet = new Set(prev);
      if (isSelected) {
        newSet.add(rowIndex);
      } else {
        newSet.delete(rowIndex);
      }
      
      if (onRowSelect) {
        const selectedData = Array.from(newSet).map(index => filteredData[index]);
        onRowSelect(selectedData);
      }
      
      return newSet;
    });
  }, [filteredData, onRowSelect]);

  const handleSelectAll = useCallback((isSelected: boolean) => {
    if (isSelected) {
      const allIndices = new Set(filteredData.map((_, index) => index));
      setSelectedRows(allIndices);
      if (onRowSelect) {
        onRowSelect(filteredData);
      }
    } else {
      setSelectedRows(new Set());
      if (onRowSelect) {
        onRowSelect([]);
      }
    }
  }, [filteredData, onRowSelect]);

  const toggleColumnVisibility = useCallback((columnKey: string) => {
    setColumns(prev =>
      prev.map(col =>
        col.key === columnKey ? { ...col, visible: !col.visible } : col
      )
    );
  }, []);

  const formatCellValue = useCallback((value: any, column: DataColumn) => {
    if (value == null) return '';
    
    if (column.format) {
      return column.format(value);
    }

    switch (column.type) {
      case 'date':
        return new Date(value).toLocaleDateString();
      case 'number':
        return typeof value === 'number' ? value.toLocaleString() : value;
      case 'boolean':
        return value ? 'Yes' : 'No';
      default:
        return String(value);
    }
  }, []);

  const handleExport = useCallback(() => {
    if (onExport) {
      onExport(selectedRows.size > 0 
        ? Array.from(selectedRows).map(index => filteredData[index])
        : filteredData
      );
    }
  }, [filteredData, selectedRows, onExport]);

  return (
    <div className={`w-full bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 ${className}`}>
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
            {title}
          </h2>
          
          <div className="flex items-center space-x-2">
            {exportable && (
              <button
                onClick={handleExport}
                className="flex items-center space-x-2 px-3 py-1.5 text-sm bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
              >
                <Download className="w-4 h-4" />
                <span>Export</span>
              </button>
            )}
            
            <button
              onClick={() => setShowColumnSettings(!showColumnSettings)}
              className="flex items-center space-x-2 px-3 py-1.5 text-sm bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors"
            >
              <MoreHorizontal className="w-4 h-4" />
              <span>Columns</span>
            </button>
          </div>
        </div>

        {/* Search and Filters */}
        <div className="flex items-center space-x-4">
          {searchable && (
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Search data..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          )}

          <div className="text-sm text-gray-500 dark:text-gray-400">
            {filteredData.length} of {data.length} rows
            {selectedRows.size > 0 && ` (${selectedRows.size} selected)`}
          </div>
        </div>

        {/* Column Settings */}
        {showColumnSettings && (
          <div className="mt-4 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <h3 className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-2">
              Column Visibility
            </h3>
            <div className="flex flex-wrap gap-2">
              {columns.map(column => (
                <button
                  key={column.key}
                  onClick={() => toggleColumnVisibility(column.key)}
                  className={`flex items-center space-x-1 px-2 py-1 text-xs rounded transition-colors ${
                    column.visible
                      ? 'bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200'
                      : 'bg-gray-200 dark:bg-gray-600 text-gray-600 dark:text-gray-400'
                  }`}
                >
                  {column.visible ? <Eye className="w-3 h-3" /> : <EyeOff className="w-3 h-3" />}
                  <span>{column.label}</span>
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Table */}
      <div 
        className="overflow-auto" 
        style={virtualScrolling ? { height } : undefined}
      >
        <table className="w-full">
          <thead className="bg-gray-50 dark:bg-gray-700 sticky top-0">
            <tr>
              {selectable && (
                <th className="w-12 px-3 py-3 text-left">
                  <input
                    type="checkbox"
                    checked={selectedRows.size === filteredData.length && filteredData.length > 0}
                    onChange={(e) => handleSelectAll(e.target.checked)}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                </th>
              )}
              
              {visibleColumns.map(column => (
                <th key={column.key} className="px-3 py-3 text-left">
                  <div className="flex items-center space-x-2">
                    <span className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      {column.label}
                    </span>
                    
                    {column.sortable !== false && (
                      <button
                        onClick={() => handleSort(column.key)}
                        className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                      >
                        {sortConfig?.key === column.key ? (
                          sortConfig.direction === 'asc' ? (
                            <ChevronUp className="w-4 h-4" />
                          ) : (
                            <ChevronDown className="w-4 h-4" />
                          )
                        ) : (
                          <ArrowUpDown className="w-4 h-4" />
                        )}
                      </button>
                    )}
                  </div>
                  
                  {column.filterable !== false && (
                    <div className="mt-1">
                      <input
                        type="text"
                        placeholder="Filter..."
                        value={filters[column.key] || ''}
                        onChange={(e) => setFilters(prev => ({ ...prev, [column.key]: e.target.value }))}
                        className="w-full px-2 py-1 text-xs border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
                      />
                    </div>
                  )}
                </th>
              ))}
            </tr>
          </thead>
          
          <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
            {paginatedData.map((row, rowIndex) => (
              <tr 
                key={rowIndex}
                className={`hover:bg-gray-50 dark:hover:bg-gray-700 ${
                  selectedRows.has(rowIndex) ? 'bg-blue-50 dark:bg-blue-950/20' : ''
                }`}
              >
                {selectable && (
                  <td className="px-3 py-3">
                    <input
                      type="checkbox"
                      checked={selectedRows.has(rowIndex)}
                      onChange={(e) => handleRowSelect(rowIndex, e.target.checked)}
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                  </td>
                )}
                
                {visibleColumns.map(column => (
                  <td key={column.key} className="px-3 py-3 text-sm text-gray-900 dark:text-gray-100">
                    {formatCellValue(row[column.key], column)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {pagination && totalPages > 1 && (
        <div className="px-4 py-3 border-t border-gray-200 dark:border-gray-700 flex items-center justify-between">
          <div className="text-sm text-gray-500 dark:text-gray-400">
            Page {currentPage} of {totalPages}
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
              disabled={currentPage === 1}
              className="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            
            <div className="flex items-center space-x-1">
              {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                const page = i + Math.max(1, currentPage - 2);
                return (
                  <button
                    key={page}
                    onClick={() => setCurrentPage(page)}
                    className={`px-3 py-1 text-sm rounded ${
                      page === currentPage
                        ? 'bg-blue-600 text-white'
                        : 'border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700'
                    }`}
                  >
                    {page}
                  </button>
                );
              })}
            </div>
            
            <button
              onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
              disabled={currentPage === totalPages}
              className="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default DataTable;
