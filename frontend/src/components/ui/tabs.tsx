'use client';

import React, { createContext, useContext, useState, useCallback, useMemo } from 'react';
import { cn } from '@/lib/utils';

interface TabsContextType {
  value: string;
  onValueChange: (value: string) => void;
}

const TabsContext = createContext<TabsContextType | undefined>(undefined);

function useTabsContext() {
  const context = useContext(TabsContext);
  if (!context) {
    throw new Error('Tabs components must be used within a Tabs provider');
  }
  return context;
}

interface TabsProps {
  readonly value?: string;
  readonly defaultValue?: string;
  readonly onValueChange?: (value: string) => void;
  readonly children: React.ReactNode;
  readonly className?: string;
}

export function Tabs({ 
  value: controlledValue, 
  defaultValue, 
  onValueChange, 
  children, 
  className 
}: TabsProps) {
  const [internalValue, setInternalValue] = useState(defaultValue ?? '');
  
  const value = controlledValue ?? internalValue;
  
  const handleValueChange = useCallback((newValue: string) => {
    if (controlledValue === undefined) {
      setInternalValue(newValue);
    }
    onValueChange?.(newValue);
  }, [controlledValue, onValueChange]);

  const contextValue = useMemo(() => ({
    value,
    onValueChange: handleValueChange
  }), [value, handleValueChange]);

  return (
    <TabsContext.Provider value={contextValue}>
      <div className={cn('tabs', className)}>
        {children}
      </div>
    </TabsContext.Provider>
  );
}

interface TabsListProps {
  readonly children: React.ReactNode;
  readonly className?: string;
}

export function TabsList({ children, className }: TabsListProps) {
  return (
    <div 
      className={cn(
        'inline-flex h-10 items-center justify-center rounded-md bg-slate-100 p-1 text-slate-500 dark:bg-slate-800 dark:text-slate-400',
        className
      )}
      role="tablist"
    >
      {children}
    </div>
  );
}

interface TabsTriggerProps {
  readonly value: string;
  readonly children: React.ReactNode;
  readonly className?: string;
  readonly disabled?: boolean;
}

export function TabsTrigger({ value, children, className, disabled }: TabsTriggerProps) {
  const { value: selectedValue, onValueChange } = useTabsContext();
  const isSelected = value === selectedValue;

  return (
    <button
      className={cn(
        'inline-flex items-center justify-center whitespace-nowrap rounded-sm px-3 py-1.5 text-sm font-medium ring-offset-white transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-950 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 data-[state=active]:bg-white data-[state=active]:text-slate-950 data-[state=active]:shadow-sm dark:ring-offset-slate-950 dark:focus-visible:ring-slate-300 dark:data-[state=active]:bg-slate-950 dark:data-[state=active]:text-slate-50',
        isSelected && 'bg-white text-slate-950 shadow-sm dark:bg-slate-950 dark:text-slate-50',
        className
      )}
      role="tab"
      aria-selected={isSelected}
      data-state={isSelected ? 'active' : 'inactive'}
      disabled={disabled}
      onClick={() => !disabled && onValueChange(value)}
    >
      {children}
    </button>
  );
}

interface TabsContentProps {
  readonly value: string;
  readonly children: React.ReactNode;
  readonly className?: string;
}

export function TabsContent({ value, children, className }: TabsContentProps) {
  const { value: selectedValue } = useTabsContext();
  const isSelected = value === selectedValue;

  if (!isSelected) {
    return null;
  }

  return (
    <div
      className={cn(
        'mt-2 ring-offset-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-950 focus-visible:ring-offset-2 dark:ring-offset-slate-950 dark:focus-visible:ring-slate-300',
        className
      )}
      role="tabpanel"
      data-state={isSelected ? 'active' : 'inactive'}
    >
      {children}
    </div>
  );
}
