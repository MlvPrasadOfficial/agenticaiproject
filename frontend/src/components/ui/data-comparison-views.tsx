'use client';

import React, { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  RotateCcw, 
  ArrowRight,
  ArrowLeft,
  TrendingUp,
  TrendingDown,
  Minus,
  Eye,
  EyeOff,
  Calendar,
  Filter,
  BarChart3,
  PieChart,
  LineChart,
  Split,
  Merge,
  Settings,
  Download,
  RefreshCw
} from 'lucide-react';

interface ComparisonData {
  id: string;
  label: string;
  data: Record<string, any>;
  timestamp?: Date;
  metadata?: Record<string, any>;
}

interface ComparisonField {
  key: string;
  label: string;
  type: 'number' | 'string' | 'date' | 'boolean' | 'percentage';
  formatter?: (value: any) => string;
  comparable?: boolean;
}

interface DataComparisonViewsProps {
  beforeData: ComparisonData[];
  afterData: ComparisonData[];
  fields: ComparisonField[];
  title?: string;
  onDataSelect?: (before: ComparisonData | null, after: ComparisonData | null) => void;
  className?: string;
}

type ViewMode = 'split' | 'overlay' | 'diff' | 'table';
type ComparisonMetric = 'value' | 'percentage' | 'absolute';

interface FieldDiff {
  field: string;
  beforeValue: any;
  afterValue: any;
  changeType: 'increased' | 'decreased' | 'unchanged' | 'new' | 'removed';
  changeValue?: number;
  changePercentage?: number;
}

export function DataComparisonViews({
  beforeData,
  afterData,
  fields,
  title = 'Data Comparison',
  onDataSelect,
  className = ''
}: DataComparisonViewsProps) {
  const [viewMode, setViewMode] = useState<ViewMode>('split');
  const [selectedBefore, setSelectedBefore] = useState<ComparisonData | null>(null);
  const [selectedAfter, setSelectedAfter] = useState<ComparisonData | null>(null);
  const [comparisonMetric, setComparisonMetric] = useState<ComparisonMetric>('value');
  const [visibleFields, setVisibleFields] = useState<Set<string>>(new Set(fields.map(f => f.key)));
  const [showOnlyChanged, setShowOnlyChanged] = useState(false);

  // Calculate differences between datasets
  const differences = useMemo(() => {
    if (!selectedBefore || !selectedAfter) return [];

    const diffs: FieldDiff[] = [];
    
    fields.forEach(field => {
      const beforeValue = selectedBefore.data[field.key];
      const afterValue = selectedAfter.data[field.key];
      
      let changeType: FieldDiff['changeType'] = 'unchanged';
      let changeValue: number | undefined;
      let changePercentage: number | undefined;

      if (beforeValue === undefined && afterValue !== undefined) {
        changeType = 'new';
      } else if (beforeValue !== undefined && afterValue === undefined) {
        changeType = 'removed';
      } else if (beforeValue !== afterValue) {
        if (field.type === 'number') {
          const numBefore = Number(beforeValue);
          const numAfter = Number(afterValue);
          changeValue = numAfter - numBefore;
          changePercentage = numBefore !== 0 ? ((numAfter - numBefore) / numBefore) * 100 : 0;
          changeType = numAfter > numBefore ? 'increased' : 'decreased';
        } else {
          changeType = beforeValue !== afterValue ? 'increased' : 'unchanged';
        }
      }

      diffs.push({
        field: field.key,
        beforeValue,
        afterValue,
        changeType,
        changeValue,
        changePercentage
      });
    });

    return diffs;
  }, [selectedBefore, selectedAfter, fields]);

  const filteredDifferences = useMemo(() => {
    let filtered = differences.filter(diff => visibleFields.has(diff.field));
    
    if (showOnlyChanged) {
      filtered = filtered.filter(diff => diff.changeType !== 'unchanged');
    }
    
    return filtered;
  }, [differences, visibleFields, showOnlyChanged]);

  const formatValue = (value: any, field: ComparisonField) => {
    if (field.formatter) {
      return field.formatter(value);
    }

    if (value === null || value === undefined) {
      return '-';
    }

    switch (field.type) {
      case 'number':
        return typeof value === 'number' ? value.toLocaleString() : String(value);
      case 'percentage':
        return `${Number(value).toFixed(2)}%`;
      case 'date':
        return new Date(value).toLocaleDateString();
      case 'boolean':
        return value ? 'Yes' : 'No';
      default:
        return String(value);
    }
  };

  const getChangeIcon = (changeType: FieldDiff['changeType']) => {
    switch (changeType) {
      case 'increased':
        return <TrendingUp className="w-4 h-4 text-green-600" />;
      case 'decreased':
        return <TrendingDown className="w-4 h-4 text-red-600" />;
      case 'new':
        return <TrendingUp className="w-4 h-4 text-blue-600" />;
      case 'removed':
        return <TrendingDown className="w-4 h-4 text-orange-600" />;
      default:
        return <Minus className="w-4 h-4 text-gray-400" />;
    }
  };

  const getChangeColor = (changeType: FieldDiff['changeType']) => {
    switch (changeType) {
      case 'increased':
        return 'text-green-600 bg-green-50 border-green-200';
      case 'decreased':
        return 'text-red-600 bg-red-50 border-red-200';
      case 'new':
        return 'text-blue-600 bg-blue-50 border-blue-200';
      case 'removed':
        return 'text-orange-600 bg-orange-50 border-orange-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const handleSelection = (before: ComparisonData | null, after: ComparisonData | null) => {
    setSelectedBefore(before);
    setSelectedAfter(after);
    onDataSelect?.(before, after);
  };

  const toggleFieldVisibility = (fieldKey: string) => {
    setVisibleFields(prev => {
      const newSet = new Set(prev);
      if (newSet.has(fieldKey)) {
        newSet.delete(fieldKey);
      } else {
        newSet.add(fieldKey);
      }
      return newSet;
    });
  };

  const renderSplitView = () => (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Before Panel */}
      <div className="space-y-4">
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 bg-red-500 rounded-full"></div>
          <h4 className="font-medium text-gray-900 dark:text-white">Before</h4>
        </div>
        
        <div className="space-y-2 max-h-64 overflow-y-auto">
          {beforeData.map(item => (
            <motion.button
              key={item.id}
              onClick={() => handleSelection(item, selectedAfter)}
              className={`w-full p-3 text-left border rounded-lg transition-colors ${
                selectedBefore?.id === item.id
                  ? 'border-red-500 bg-red-50 dark:bg-red-900/20'
                  : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
              }`}
              whileHover={{ scale: 1.02 }}
            >
              <div className="font-medium text-gray-900 dark:text-white">{item.label}</div>
              {item.timestamp && (
                <div className="text-sm text-gray-500 dark:text-gray-400">
                  {item.timestamp.toLocaleString()}
                </div>
              )}
            </motion.button>
          ))}
        </div>
      </div>

      {/* After Panel */}
      <div className="space-y-4">
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 bg-green-500 rounded-full"></div>
          <h4 className="font-medium text-gray-900 dark:text-white">After</h4>
        </div>
        
        <div className="space-y-2 max-h-64 overflow-y-auto">
          {afterData.map(item => (
            <motion.button
              key={item.id}
              onClick={() => handleSelection(selectedBefore, item)}
              className={`w-full p-3 text-left border rounded-lg transition-colors ${
                selectedAfter?.id === item.id
                  ? 'border-green-500 bg-green-50 dark:bg-green-900/20'
                  : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
              }`}
              whileHover={{ scale: 1.02 }}
            >
              <div className="font-medium text-gray-900 dark:text-white">{item.label}</div>
              {item.timestamp && (
                <div className="text-sm text-gray-500 dark:text-gray-400">
                  {item.timestamp.toLocaleString()}
                </div>
              )}
            </motion.button>
          ))}
        </div>
      </div>
    </div>
  );

  const renderDiffView = () => (
    <div className="space-y-4">
      {filteredDifferences.map(diff => {
        const field = fields.find(f => f.key === diff.field);
        if (!field) return null;

        return (
          <motion.div
            key={diff.field}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className={`p-4 border rounded-lg ${getChangeColor(diff.changeType)}`}
          >
            <div className="flex items-start justify-between">
              <div className="flex items-center space-x-3">
                {getChangeIcon(diff.changeType)}
                <div>
                  <h5 className="font-medium">{field.label}</h5>
                  <div className="flex items-center space-x-4 mt-1">
                    <span className="text-sm">
                      Before: <strong>{formatValue(diff.beforeValue, field)}</strong>
                    </span>
                    <ArrowRight className="w-4 h-4" />
                    <span className="text-sm">
                      After: <strong>{formatValue(diff.afterValue, field)}</strong>
                    </span>
                  </div>
                </div>
              </div>
              
              {diff.changeValue !== undefined && (
                <div className="text-right">
                  <div className="text-sm font-medium">
                    {diff.changeValue > 0 ? '+' : ''}{diff.changeValue.toLocaleString()}
                  </div>
                  {diff.changePercentage !== undefined && (
                    <div className="text-xs">
                      ({diff.changePercentage > 0 ? '+' : ''}{diff.changePercentage.toFixed(1)}%)
                    </div>
                  )}
                </div>
              )}
            </div>
          </motion.div>
        );
      })}
    </div>
  );

  const renderTableView = () => (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b border-gray-200 dark:border-gray-700">
            <th className="text-left py-3 px-4 font-medium text-gray-900 dark:text-white">Field</th>
            <th className="text-left py-3 px-4 font-medium text-gray-900 dark:text-white">Before</th>
            <th className="text-left py-3 px-4 font-medium text-gray-900 dark:text-white">After</th>
            <th className="text-left py-3 px-4 font-medium text-gray-900 dark:text-white">Change</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
          {filteredDifferences.map(diff => {
            const field = fields.find(f => f.key === diff.field);
            if (!field) return null;

            return (
              <tr key={diff.field} className="hover:bg-gray-50 dark:hover:bg-gray-800">
                <td className="py-3 px-4">
                  <div className="flex items-center space-x-2">
                    {getChangeIcon(diff.changeType)}
                    <span className="font-medium text-gray-900 dark:text-white">
                      {field.label}
                    </span>
                  </div>
                </td>
                <td className="py-3 px-4 text-gray-600 dark:text-gray-300">
                  {formatValue(diff.beforeValue, field)}
                </td>
                <td className="py-3 px-4 text-gray-600 dark:text-gray-300">
                  {formatValue(diff.afterValue, field)}
                </td>
                <td className="py-3 px-4">
                  {diff.changeValue !== undefined && (
                    <div>
                      <span className={`font-medium ${
                        diff.changeValue > 0 ? 'text-green-600' : 
                        diff.changeValue < 0 ? 'text-red-600' : 'text-gray-600'
                      }`}>
                        {diff.changeValue > 0 ? '+' : ''}{diff.changeValue.toLocaleString()}
                      </span>
                      {diff.changePercentage !== undefined && (
                        <span className="text-sm text-gray-500 ml-2">
                          ({diff.changePercentage > 0 ? '+' : ''}{diff.changePercentage.toFixed(1)}%)
                        </span>
                      )}
                    </div>
                  )}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );

  return (
    <div className={`bg-white dark:bg-gray-900 rounded-xl shadow-lg overflow-hidden ${className}`}>
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            {title}
          </h3>
          
          <div className="flex items-center space-x-2">
            {/* View Mode Selector */}
            <div className="flex bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
              <button
                onClick={() => setViewMode('split')}
                className={`px-3 py-1 text-sm rounded-md transition-colors ${
                  viewMode === 'split' 
                    ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow' 
                    : 'text-gray-600 dark:text-gray-400'
                }`}
              >
                <Split className="w-4 h-4" />
              </button>
              <button
                onClick={() => setViewMode('diff')}
                className={`px-3 py-1 text-sm rounded-md transition-colors ${
                  viewMode === 'diff' 
                    ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow' 
                    : 'text-gray-600 dark:text-gray-400'
                }`}
              >
                <BarChart3 className="w-4 h-4" />
              </button>
              <button
                onClick={() => setViewMode('table')}
                className={`px-3 py-1 text-sm rounded-md transition-colors ${
                  viewMode === 'table' 
                    ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow' 
                    : 'text-gray-600 dark:text-gray-400'
                }`}
              >
                <PieChart className="w-4 h-4" />
              </button>
            </div>

            {/* Controls */}
            <button
              onClick={() => setShowOnlyChanged(!showOnlyChanged)}
              className={`px-3 py-1 text-sm rounded-md transition-colors ${
                showOnlyChanged 
                  ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400' 
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200'
              }`}
            >
              {showOnlyChanged ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
            </button>
          </div>
        </div>

        {/* Field Visibility Controls */}
        <div className="mt-4 flex flex-wrap gap-2">
          {fields.map(field => (
            <button
              key={field.key}
              onClick={() => toggleFieldVisibility(field.key)}
              className={`px-2 py-1 text-xs rounded-full border transition-colors ${
                visibleFields.has(field.key)
                  ? 'bg-blue-100 text-blue-800 border-blue-200'
                  : 'bg-gray-100 text-gray-600 border-gray-200 hover:bg-gray-200'
              }`}
            >
              {field.label}
            </button>
          ))}
        </div>

        {/* Selection Summary */}
        {selectedBefore && selectedAfter && (
          <div className="mt-4 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600 dark:text-gray-400">
                Comparing: <strong>{selectedBefore.label}</strong> vs <strong>{selectedAfter.label}</strong>
              </span>
              <span className="text-gray-500 dark:text-gray-400">
                {filteredDifferences.filter(d => d.changeType !== 'unchanged').length} changes
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Content */}
      <div className="p-6">
        {viewMode === 'split' && renderSplitView()}
        
        <AnimatePresence>
          {(viewMode === 'diff' || viewMode === 'table') && selectedBefore && selectedAfter && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              {viewMode === 'diff' && renderDiffView()}
              {viewMode === 'table' && renderTableView()}
            </motion.div>
          )}
        </AnimatePresence>

        {(viewMode === 'diff' || viewMode === 'table') && (!selectedBefore || !selectedAfter) && (
          <div className="text-center py-8 text-gray-500 dark:text-gray-400">
            <Split className="w-8 h-8 mx-auto mb-2" />
            <p>Select items from both before and after datasets to compare</p>
          </div>
        )}
      </div>
    </div>
  );
}
