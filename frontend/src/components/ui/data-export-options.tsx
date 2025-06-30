'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Download, 
  FileText, 
  Table, 
  FileSpreadsheet,
  Code,
  Image,
  Share2,
  Settings,
  Calendar,
  Filter,
  Eye,
  Loader2,
  CheckCircle,
  XCircle,
  Info
} from 'lucide-react';

export interface ExportFormat {
  id: string;
  name: string;
  description: string;
  icon: React.ComponentType<any>;
  extension: string;
  mimeType: string;
  options?: ExportOption[];
}

export interface ExportOption {
  key: string;
  label: string;
  type: 'boolean' | 'select' | 'range' | 'text';
  defaultValue: any;
  options?: Array<{ value: any; label: string }>;
}

interface DataExportOptionsProps {
  data: any[];
  columns?: Array<{ key: string; label: string }>;
  selectedRows?: any[];
  onExport: (format: string, options: Record<string, any>) => Promise<void>;
  className?: string;
}

const EXPORT_FORMATS: ExportFormat[] = [
  {
    id: 'csv',
    name: 'CSV',
    description: 'Comma-separated values for spreadsheet applications',
    icon: Table,
    extension: 'csv',
    mimeType: 'text/csv',
    options: [
      {
        key: 'delimiter',
        label: 'Delimiter',
        type: 'select',
        defaultValue: ',',
        options: [
          { value: ',', label: 'Comma (,)' },
          { value: ';', label: 'Semicolon (;)' },
          { value: '\t', label: 'Tab' },
          { value: '|', label: 'Pipe (|)' }
        ]
      },
      {
        key: 'includeHeaders',
        label: 'Include column headers',
        type: 'boolean',
        defaultValue: true
      },
      {
        key: 'encoding',
        label: 'Text encoding',
        type: 'select',
        defaultValue: 'utf-8',
        options: [
          { value: 'utf-8', label: 'UTF-8' },
          { value: 'iso-8859-1', label: 'ISO-8859-1' },
          { value: 'windows-1252', label: 'Windows-1252' }
        ]
      }
    ]
  },
  {
    id: 'xlsx',
    name: 'Excel',
    description: 'Microsoft Excel spreadsheet with formatting',
    icon: FileSpreadsheet,
    extension: 'xlsx',
    mimeType: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    options: [
      {
        key: 'sheetName',
        label: 'Sheet name',
        type: 'text',
        defaultValue: 'Data Export'
      },
      {
        key: 'includeFormatting',
        label: 'Include cell formatting',
        type: 'boolean',
        defaultValue: true
      },
      {
        key: 'autoFitColumns',
        label: 'Auto-fit column widths',
        type: 'boolean',
        defaultValue: true
      },
      {
        key: 'freezeHeader',
        label: 'Freeze header row',
        type: 'boolean',
        defaultValue: true
      }
    ]
  },
  {
    id: 'json',
    name: 'JSON',
    description: 'JavaScript Object Notation for data interchange',
    icon: Code,
    extension: 'json',
    mimeType: 'application/json',
    options: [
      {
        key: 'pretty',
        label: 'Pretty print (formatted)',
        type: 'boolean',
        defaultValue: true
      },
      {
        key: 'includeMetadata',
        label: 'Include export metadata',
        type: 'boolean',
        defaultValue: false
      }
    ]
  },
  {
    id: 'pdf',
    name: 'PDF',
    description: 'Portable Document Format for reports',
    icon: FileText,
    extension: 'pdf',
    mimeType: 'application/pdf',
    options: [
      {
        key: 'orientation',
        label: 'Page orientation',
        type: 'select',
        defaultValue: 'portrait',
        options: [
          { value: 'portrait', label: 'Portrait' },
          { value: 'landscape', label: 'Landscape' }
        ]
      },
      {
        key: 'pageSize',
        label: 'Page size',
        type: 'select',
        defaultValue: 'A4',
        options: [
          { value: 'A4', label: 'A4' },
          { value: 'A3', label: 'A3' },
          { value: 'Letter', label: 'Letter' },
          { value: 'Legal', label: 'Legal' }
        ]
      },
      {
        key: 'includeTitle',
        label: 'Include title page',
        type: 'boolean',
        defaultValue: true
      },
      {
        key: 'fontSize',
        label: 'Font size',
        type: 'select',
        defaultValue: '10',
        options: [
          { value: '8', label: '8pt' },
          { value: '10', label: '10pt' },
          { value: '12', label: '12pt' },
          { value: '14', label: '14pt' }
        ]
      }
    ]
  },
  {
    id: 'png',
    name: 'Image (PNG)',
    description: 'Portable Network Graphics image format',
    icon: Image,
    extension: 'png',
    mimeType: 'image/png',
    options: [
      {
        key: 'resolution',
        label: 'Resolution (DPI)',
        type: 'select',
        defaultValue: '150',
        options: [
          { value: '72', label: '72 (Screen)' },
          { value: '150', label: '150 (High Quality)' },
          { value: '300', label: '300 (Print Quality)' }
        ]
      },
      {
        key: 'includeBackground',
        label: 'Include background',
        type: 'boolean',
        defaultValue: true
      }
    ]
  }
];

export function DataExportOptions({
  data,
  columns = [],
  selectedRows,
  onExport,
  className = ''
}: DataExportOptionsProps) {
  const [selectedFormat, setSelectedFormat] = useState<ExportFormat>(EXPORT_FORMATS[0]);
  const [exportOptions, setExportOptions] = useState<Record<string, any>>({});
  const [exportScope, setExportScope] = useState<'all' | 'selected' | 'filtered'>('all');
  const [isExporting, setIsExporting] = useState(false);
  const [exportStatus, setExportStatus] = useState<{
    type: 'success' | 'error' | null;
    message: string;
  }>({ type: null, message: '' });
  const [showAdvanced, setShowAdvanced] = useState(false);

  // Initialize export options when format changes
  React.useEffect(() => {
    const options: Record<string, any> = {};
    selectedFormat.options?.forEach(option => {
      options[option.key] = option.defaultValue;
    });
    setExportOptions(options);
  }, [selectedFormat]);

  const handleExport = async () => {
    setIsExporting(true);
    setExportStatus({ type: null, message: '' });

    try {
      const exportData = {
        format: selectedFormat.id,
        scope: exportScope,
        options: exportOptions,
        data: exportScope === 'selected' ? selectedRows || [] : data,
        columns: columns,
        timestamp: new Date().toISOString()
      };

      await onExport(selectedFormat.id, exportData);
      
      setExportStatus({
        type: 'success',
        message: `Successfully exported ${exportData.data.length} rows as ${selectedFormat.name}`
      });
    } catch (error) {
      setExportStatus({
        type: 'error',
        message: `Export failed: ${error instanceof Error ? error.message : 'Unknown error'}`
      });
    } finally {
      setIsExporting(false);
    }
  };

  const updateOption = (key: string, value: any) => {
    setExportOptions(prev => ({ ...prev, [key]: value }));
  };

  const renderOptionInput = (option: ExportOption) => {
    const value = exportOptions[option.key];

    switch (option.type) {
      case 'boolean':
        return (
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={value}
              onChange={(e) => updateOption(option.key, e.target.checked)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="text-sm text-gray-700 dark:text-gray-300">
              {option.label}
            </span>
          </label>
        );

      case 'select':
        return (
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              {option.label}
            </label>
            <select
              value={value}
              onChange={(e) => updateOption(option.key, e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
            >
              {option.options?.map(opt => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>
        );

      case 'text':
        return (
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              {option.label}
            </label>
            <input
              type="text"
              value={value}
              onChange={(e) => updateOption(option.key, e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
            />
          </div>
        );

      default:
        return null;
    }
  };

  const getDataCount = () => {
    switch (exportScope) {
      case 'selected':
        return selectedRows?.length || 0;
      case 'filtered':
        return data.length; // Assuming data is already filtered
      case 'all':
      default:
        return data.length;
    }
  };

  return (
    <div className={`bg-white dark:bg-gray-900 rounded-xl shadow-lg overflow-hidden ${className}`}>
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Download className="w-5 h-5 text-gray-500 dark:text-gray-400" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Export Data
            </h3>
          </div>
          
          <button
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="flex items-center space-x-2 px-3 py-1 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-800"
          >
            <Settings className="w-4 h-4" />
            <span>Advanced</span>
          </button>
        </div>
      </div>

      <div className="p-6">
        {/* Export Status */}
        <AnimatePresence>
          {exportStatus.type && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className={`mb-4 p-3 rounded-lg flex items-center space-x-2 ${
                exportStatus.type === 'success' 
                  ? 'bg-green-50 text-green-800 border border-green-200' 
                  : 'bg-red-50 text-red-800 border border-red-200'
              }`}
            >
              {exportStatus.type === 'success' ? (
                <CheckCircle className="w-4 h-4" />
              ) : (
                <XCircle className="w-4 h-4" />
              )}
              <span className="text-sm">{exportStatus.message}</span>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Format Selection */}
        <div className="mb-6">
          <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
            Select Export Format
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {EXPORT_FORMATS.map((format) => {
              const Icon = format.icon;
              return (
                <motion.button
                  key={format.id}
                  onClick={() => setSelectedFormat(format)}
                  className={`p-4 border-2 rounded-lg text-left transition-all ${
                    selectedFormat.id === format.id
                      ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                      : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                  }`}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <div className="flex items-center space-x-3 mb-2">
                    <Icon className={`w-5 h-5 ${
                      selectedFormat.id === format.id 
                        ? 'text-blue-600 dark:text-blue-400' 
                        : 'text-gray-500 dark:text-gray-400'
                    }`} />
                    <span className="font-medium text-gray-900 dark:text-white">
                      {format.name}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {format.description}
                  </p>
                </motion.button>
              );
            })}
          </div>
        </div>

        {/* Export Scope */}
        <div className="mb-6">
          <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
            Data to Export
          </h4>
          <div className="space-y-2">
            <label className="flex items-center space-x-3">
              <input
                type="radio"
                name="exportScope"
                value="all"
                checked={exportScope === 'all'}
                onChange={(e) => setExportScope(e.target.value as any)}
                className="text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700 dark:text-gray-300">
                All data ({data.length} rows)
              </span>
            </label>
            
            {selectedRows && selectedRows.length > 0 && (
              <label className="flex items-center space-x-3">
                <input
                  type="radio"
                  name="exportScope"
                  value="selected"
                  checked={exportScope === 'selected'}
                  onChange={(e) => setExportScope(e.target.value as any)}
                  className="text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700 dark:text-gray-300">
                  Selected rows ({selectedRows.length} rows)
                </span>
              </label>
            )}
            
            <label className="flex items-center space-x-3">
              <input
                type="radio"
                name="exportScope"
                value="filtered"
                checked={exportScope === 'filtered'}
                onChange={(e) => setExportScope(e.target.value as any)}
                className="text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700 dark:text-gray-300">
                Current filtered view ({data.length} rows)
              </span>
            </label>
          </div>
        </div>

        {/* Format Options */}
        {selectedFormat.options && selectedFormat.options.length > 0 && (
          <div className="mb-6">
            <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
              Export Options
            </h4>
            <div className="space-y-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
              {selectedFormat.options.map(option => (
                <div key={option.key}>
                  {renderOptionInput(option)}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Advanced Options */}
        <AnimatePresence>
          {showAdvanced && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mb-6"
            >
              <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
                Advanced Options
              </h4>
              <div className="space-y-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    File name prefix
                  </label>
                  <input
                    type="text"
                    placeholder="export"
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
                  />
                </div>
                
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-700 dark:text-gray-300">
                    Include timestamp in filename
                  </span>
                </label>
                
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-700 dark:text-gray-300">
                    Compress output file (.zip)
                  </span>
                </label>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Export Summary */}
        <div className="mb-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-700">
          <div className="flex items-start space-x-2">
            <Info className="w-4 h-4 text-blue-600 dark:text-blue-400 mt-0.5" />
            <div>
              <p className="text-sm text-blue-800 dark:text-blue-200">
                <strong>Export Summary:</strong> {getDataCount()} rows will be exported as {selectedFormat.name} ({selectedFormat.extension.toUpperCase()})
              </p>
              {columns.length > 0 && (
                <p className="text-xs text-blue-700 dark:text-blue-300 mt-1">
                  Columns: {columns.map(col => col.label).join(', ')}
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Export Button */}
        <motion.button
          onClick={handleExport}
          disabled={isExporting || getDataCount() === 0}
          className={`w-full py-3 px-4 rounded-lg font-medium transition-colors flex items-center justify-center space-x-2 ${
            isExporting || getDataCount() === 0
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-blue-600 hover:bg-blue-700 text-white shadow-lg hover:shadow-xl'
          }`}
          whileHover={!isExporting && getDataCount() > 0 ? { scale: 1.02 } : {}}
          whileTap={!isExporting && getDataCount() > 0 ? { scale: 0.98 } : {}}
        >
          {isExporting ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Exporting...</span>
            </>
          ) : (
            <>
              <Download className="w-4 h-4" />
              <span>Export {getDataCount()} rows as {selectedFormat.name}</span>
            </>
          )}
        </motion.button>
      </div>
    </div>
  );
}
