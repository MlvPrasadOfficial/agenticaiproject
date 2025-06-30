'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  X, 
  Plus, 
  Filter,
  Search,
  Calendar,
  Hash,
  Type,
  ToggleLeft,
  ToggleRight,
  ChevronDown,
  Trash2,
  RotateCcw,
  Save,
  Settings
} from 'lucide-react';

export interface FilterCondition {
  id: string;
  field: string;
  operator: string;
  value: any;
  type: 'string' | 'number' | 'date' | 'boolean' | 'select';
}

export interface FilterGroup {
  id: string;
  name: string;
  conditions: FilterCondition[];
  operator: 'AND' | 'OR';
  color?: string;
}

interface DataFilteringInterfaceProps {
  fields: Array<{
    key: string;
    label: string;
    type: 'string' | 'number' | 'date' | 'boolean' | 'select';
    options?: Array<{ value: any; label: string }>;
  }>;
  onFiltersChange: (filters: FilterGroup[]) => void;
  savedFilters?: FilterGroup[];
  onSaveFilter?: (filter: FilterGroup) => void;
  className?: string;
}

const OPERATORS = {
  string: [
    { value: 'contains', label: 'Contains' },
    { value: 'equals', label: 'Equals' },
    { value: 'startsWith', label: 'Starts with' },
    { value: 'endsWith', label: 'Ends with' },
    { value: 'isEmpty', label: 'Is empty' },
    { value: 'isNotEmpty', label: 'Is not empty' }
  ],
  number: [
    { value: 'equals', label: 'Equals' },
    { value: 'greaterThan', label: 'Greater than' },
    { value: 'lessThan', label: 'Less than' },
    { value: 'greaterThanOrEqual', label: 'Greater than or equal' },
    { value: 'lessThanOrEqual', label: 'Less than or equal' },
    { value: 'between', label: 'Between' }
  ],
  date: [
    { value: 'equals', label: 'On' },
    { value: 'after', label: 'After' },
    { value: 'before', label: 'Before' },
    { value: 'between', label: 'Between' },
    { value: 'isToday', label: 'Is today' },
    { value: 'isThisWeek', label: 'Is this week' },
    { value: 'isThisMonth', label: 'Is this month' }
  ],
  boolean: [
    { value: 'equals', label: 'Is' }
  ],
  select: [
    { value: 'equals', label: 'Equals' },
    { value: 'in', label: 'Is one of' },
    { value: 'notIn', label: 'Is not one of' }
  ]
};

const CHIP_COLORS = [
  'bg-blue-100 text-blue-800 border-blue-200',
  'bg-green-100 text-green-800 border-green-200',
  'bg-purple-100 text-purple-800 border-purple-200',
  'bg-orange-100 text-orange-800 border-orange-200',
  'bg-pink-100 text-pink-800 border-pink-200',
  'bg-indigo-100 text-indigo-800 border-indigo-200'
];

export function DataFilteringInterface({
  fields,
  onFiltersChange,
  savedFilters = [],
  onSaveFilter,
  className = ''
}: DataFilteringInterfaceProps) {
  const [filterGroups, setFilterGroups] = useState<FilterGroup[]>([]);
  const [showAddCondition, setShowAddCondition] = useState<string | null>(null);
  const [quickSearch, setQuickSearch] = useState('');
  const [showSavedFilters, setShowSavedFilters] = useState(false);

  // Initialize with default filter group
  useEffect(() => {
    if (filterGroups.length === 0) {
      setFilterGroups([{
        id: '1',
        name: 'Default Filter',
        conditions: [],
        operator: 'AND',
        color: CHIP_COLORS[0]
      }]);
    }
  }, []);

  // Notify parent of filter changes
  useEffect(() => {
    onFiltersChange(filterGroups);
  }, [filterGroups, onFiltersChange]);

  const addFilterGroup = () => {
    const newGroup: FilterGroup = {
      id: Date.now().toString(),
      name: `Filter Group ${filterGroups.length + 1}`,
      conditions: [],
      operator: 'AND',
      color: CHIP_COLORS[filterGroups.length % CHIP_COLORS.length]
    };
    setFilterGroups(prev => [...prev, newGroup]);
  };

  const removeFilterGroup = (groupId: string) => {
    setFilterGroups(prev => prev.filter(group => group.id !== groupId));
  };

  const updateFilterGroup = (groupId: string, updates: Partial<FilterGroup>) => {
    setFilterGroups(prev => prev.map(group => 
      group.id === groupId ? { ...group, ...updates } : group
    ));
  };

  const addCondition = (groupId: string) => {
    const newCondition: FilterCondition = {
      id: Date.now().toString(),
      field: fields[0]?.key || '',
      operator: 'contains',
      value: '',
      type: fields[0]?.type || 'string'
    };

    setFilterGroups(prev => prev.map(group => 
      group.id === groupId 
        ? { ...group, conditions: [...group.conditions, newCondition] }
        : group
    ));
    setShowAddCondition(null);
  };

  const removeCondition = (groupId: string, conditionId: string) => {
    setFilterGroups(prev => prev.map(group => 
      group.id === groupId 
        ? { ...group, conditions: group.conditions.filter(c => c.id !== conditionId) }
        : group
    ));
  };

  const updateCondition = (groupId: string, conditionId: string, updates: Partial<FilterCondition>) => {
    setFilterGroups(prev => prev.map(group => 
      group.id === groupId 
        ? {
            ...group,
            conditions: group.conditions.map(condition =>
              condition.id === conditionId ? { ...condition, ...updates } : condition
            )
          }
        : group
    ));
  };

  const clearAllFilters = () => {
    setFilterGroups([{
      id: '1',
      name: 'Default Filter',
      conditions: [],
      operator: 'AND',
      color: CHIP_COLORS[0]
    }]);
    setQuickSearch('');
  };

  const getFieldByKey = (key: string) => fields.find(f => f.key === key);

  const renderConditionValue = (groupId: string, condition: FilterCondition) => {
    const field = getFieldByKey(condition.field);
    if (!field) return null;

    const updateValue = (value: any) => {
      updateCondition(groupId, condition.id, { value });
    };

    switch (field.type) {
      case 'string':
        if (['isEmpty', 'isNotEmpty'].includes(condition.operator)) {
          return null;
        }
        return (
          <input
            type="text"
            value={condition.value}
            onChange={(e) => updateValue(e.target.value)}
            placeholder="Enter value"
            className="px-3 py-1 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
          />
        );

      case 'number':
        if (condition.operator === 'between') {
          return (
            <div className="flex items-center space-x-2">
              <input
                type="number"
                value={condition.value?.min || ''}
                onChange={(e) => updateValue({ ...condition.value, min: e.target.value })}
                placeholder="Min"
                className="px-3 py-1 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm w-20"
              />
              <span className="text-gray-500">and</span>
              <input
                type="number"
                value={condition.value?.max || ''}
                onChange={(e) => updateValue({ ...condition.value, max: e.target.value })}
                placeholder="Max"
                className="px-3 py-1 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm w-20"
              />
            </div>
          );
        }
        return (
          <input
            type="number"
            value={condition.value}
            onChange={(e) => updateValue(e.target.value)}
            placeholder="Enter number"
            className="px-3 py-1 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
          />
        );

      case 'date':
        if (['isToday', 'isThisWeek', 'isThisMonth'].includes(condition.operator)) {
          return null;
        }
        if (condition.operator === 'between') {
          return (
            <div className="flex items-center space-x-2">
              <input
                type="date"
                value={condition.value?.start || ''}
                onChange={(e) => updateValue({ ...condition.value, start: e.target.value })}
                className="px-3 py-1 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
              />
              <span className="text-gray-500">and</span>
              <input
                type="date"
                value={condition.value?.end || ''}
                onChange={(e) => updateValue({ ...condition.value, end: e.target.value })}
                className="px-3 py-1 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
              />
            </div>
          );
        }
        return (
          <input
            type="date"
            value={condition.value}
            onChange={(e) => updateValue(e.target.value)}
            className="px-3 py-1 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
          />
        );

      case 'boolean':
        return (
          <select
            value={condition.value}
            onChange={(e) => updateValue(e.target.value === 'true')}
            className="px-3 py-1 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
          >
            <option value="true">True</option>
            <option value="false">False</option>
          </select>
        );

      case 'select':
        if (['in', 'notIn'].includes(condition.operator)) {
          return (
            <select
              multiple
              value={condition.value || []}
              onChange={(e) => updateValue(Array.from(e.target.selectedOptions, option => option.value))}
              className="px-3 py-1 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
            >
              {field.options?.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          );
        }
        return (
          <select
            value={condition.value}
            onChange={(e) => updateValue(e.target.value)}
            className="px-3 py-1 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
          >
            <option value="">Select option</option>
            {field.options?.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        );

      default:
        return null;
    }
  };

  const getActiveFiltersCount = () => {
    return filterGroups.reduce((count, group) => count + group.conditions.length, 0);
  };

  return (
    <div className={`bg-white dark:bg-gray-900 rounded-xl shadow-lg overflow-hidden ${className}`}>
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Filter className="w-5 h-5 text-gray-500 dark:text-gray-400" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Data Filters
            </h3>
            {getActiveFiltersCount() > 0 && (
              <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                {getActiveFiltersCount()} active
              </span>
            )}
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setShowSavedFilters(!showSavedFilters)}
              className="px-3 py-1 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-800"
            >
              <Save className="w-4 h-4 mr-1 inline" />
              Saved
            </button>
            <button
              onClick={clearAllFilters}
              className="px-3 py-1 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-800"
            >
              <RotateCcw className="w-4 h-4 mr-1 inline" />
              Clear All
            </button>
          </div>
        </div>

        {/* Quick Search */}
        <div className="mt-4 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Quick search across all fields..."
            value={quickSearch}
            onChange={(e) => setQuickSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Saved Filters */}
        <AnimatePresence>
          {showSavedFilters && savedFilters.length > 0 && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mt-4 flex flex-wrap gap-2"
            >
              {savedFilters.map(filter => (
                <button
                  key={filter.id}
                  onClick={() => setFilterGroups([filter])}
                  className={`px-3 py-1 text-sm rounded-full border ${filter.color || CHIP_COLORS[0]} hover:shadow-md transition-shadow`}
                >
                  {filter.name}
                </button>
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Filter Groups */}
      <div className="p-6 space-y-4">
        {filterGroups.map((group, groupIndex) => (
          <motion.div
            key={group.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="border border-gray-200 dark:border-gray-700 rounded-lg p-4"
          >
            {/* Group Header */}
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-3">
                <input
                  type="text"
                  value={group.name}
                  onChange={(e) => updateFilterGroup(group.id, { name: e.target.value })}
                  className="font-medium text-gray-900 dark:text-white bg-transparent border-none focus:outline-none focus:ring-0"
                />
                
                <select
                  value={group.operator}
                  onChange={(e) => updateFilterGroup(group.id, { operator: e.target.value as 'AND' | 'OR' })}
                  className="px-2 py-1 text-xs border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                >
                  <option value="AND">AND</option>
                  <option value="OR">OR</option>
                </select>
              </div>
              
              <div className="flex items-center space-x-2">
                {onSaveFilter && (
                  <button
                    onClick={() => onSaveFilter(group)}
                    className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                  >
                    <Save className="w-4 h-4" />
                  </button>
                )}
                
                {filterGroups.length > 1 && (
                  <button
                    onClick={() => removeFilterGroup(group.id)}
                    className="p-1 text-gray-400 hover:text-red-600 dark:hover:text-red-400"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                )}
              </div>
            </div>

            {/* Conditions */}
            <div className="space-y-2">
              {group.conditions.map((condition, conditionIndex) => (
                <motion.div
                  key={condition.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="flex items-center space-x-2 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg"
                >
                  {conditionIndex > 0 && (
                    <span className="text-sm text-gray-500 dark:text-gray-400 font-medium px-2">
                      {group.operator}
                    </span>
                  )}
                  
                  {/* Field Select */}
                  <select
                    value={condition.field}
                    onChange={(e) => {
                      const field = getFieldByKey(e.target.value);
                      if (field) {
                        updateCondition(group.id, condition.id, {
                          field: e.target.value,
                          type: field.type,
                          operator: OPERATORS[field.type][0].value,
                          value: ''
                        });
                      }
                    }}
                    className="px-3 py-1 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
                  >
                    {fields.map(field => (
                      <option key={field.key} value={field.key}>
                        {field.label}
                      </option>
                    ))}
                  </select>

                  {/* Operator Select */}
                  <select
                    value={condition.operator}
                    onChange={(e) => updateCondition(group.id, condition.id, { operator: e.target.value, value: '' })}
                    className="px-3 py-1 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
                  >
                    {OPERATORS[condition.type]?.map(op => (
                      <option key={op.value} value={op.value}>
                        {op.label}
                      </option>
                    ))}
                  </select>

                  {/* Value Input */}
                  {renderConditionValue(group.id, condition)}

                  {/* Remove Condition */}
                  <button
                    onClick={() => removeCondition(group.id, condition.id)}
                    className="p-1 text-gray-400 hover:text-red-600 dark:hover:text-red-400"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </motion.div>
              ))}

              {/* Add Condition Button */}
              <button
                onClick={() => addCondition(group.id)}
                className="flex items-center space-x-2 px-3 py-2 text-sm text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg border-2 border-dashed border-blue-300 dark:border-blue-600 w-full"
              >
                <Plus className="w-4 h-4" />
                <span>Add Condition</span>
              </button>
            </div>
          </motion.div>
        ))}

        {/* Add Filter Group */}
        <motion.button
          onClick={addFilterGroup}
          className="flex items-center justify-center space-x-2 px-4 py-3 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 w-full"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <Plus className="w-4 h-4" />
          <span>Add Filter Group</span>
        </motion.button>
      </div>
    </div>
  );
}
