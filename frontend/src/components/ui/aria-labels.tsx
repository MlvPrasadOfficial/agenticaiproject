'use client';

import React, { createContext, useContext, ReactNode, ReactElement, cloneElement, isValidElement } from 'react';

// ARIA Label Provider Context
interface AriaLabelsContextType {
  generateId: (prefix?: string) => string;
  registerLabel: (id: string, label: string) => void;
  getLabel: (id: string) => string | undefined;
  labeledBy: (id: string, fallback?: string) => { 'aria-labelledby': string };
  describedBy: (id: string, fallback?: string) => { 'aria-describedby': string };
}

const AriaLabelsContext = createContext<AriaLabelsContextType | null>(null);

// Provider Component
interface AriaLabelsProviderProps {
  children: ReactNode;
}

export function AriaLabelsProvider({ children }: AriaLabelsProviderProps) {
  const [labels] = React.useState<Map<string, string>>(new Map());
  const [idCounter, setIdCounter] = React.useState(0);

  const generateId = (prefix = 'aria') => {
    const id = `${prefix}-${idCounter}`;
    setIdCounter(prev => prev + 1);
    return id;
  };

  const registerLabel = (id: string, label: string) => {
    labels.set(id, label);
  };

  const getLabel = (id: string) => {
    return labels.get(id);
  };

  const labeledBy = (id: string, fallback?: string) => ({
    'aria-labelledby': id,
    ...(fallback && { 'aria-label': fallback })
  });

  const describedBy = (id: string, fallback?: string) => ({
    'aria-describedby': id,
    ...(fallback && { 'aria-label': fallback })
  });

  return (
    <AriaLabelsContext.Provider
      value={{
        generateId,
        registerLabel,
        getLabel,
        labeledBy,
        describedBy
      }}
    >
      {children}
    </AriaLabelsContext.Provider>
  );
}

// Hook to use ARIA Labels
export function useAriaLabels() {
  const context = useContext(AriaLabelsContext);
  if (!context) {
    throw new Error('useAriaLabels must be used within an AriaLabelsProvider');
  }
  return context;
}

// Common ARIA Label Components

// Labeled Component - Adds comprehensive ARIA labeling
interface LabeledProps {
  children: ReactElement;
  label: string;
  description?: string;
  required?: boolean;
  invalid?: boolean;
  expanded?: boolean;
  controls?: string;
  owns?: string;
  level?: number;
  role?: string;
  live?: 'off' | 'polite' | 'assertive';
}

export function Labeled({
  children,
  label,
  description,
  required = false,
  invalid = false,
  expanded,
  controls,
  owns,
  level,
  role,
  live
}: LabeledProps) {
  const { generateId } = useAriaLabels();
  
  const labelId = generateId('label');
  const descId = description ? generateId('desc') : undefined;
  
  const ariaProps: Record<string, any> = {
    'aria-label': label,
    'aria-labelledby': labelId,
    ...(descId && { 'aria-describedby': descId }),
    ...(required && { 'aria-required': true }),
    ...(invalid && { 'aria-invalid': true }),
    ...(expanded !== undefined && { 'aria-expanded': expanded }),
    ...(controls && { 'aria-controls': controls }),
    ...(owns && { 'aria-owns': owns }),
    ...(level && { 'aria-level': level }),
    ...(role && { role }),
    ...(live && { 'aria-live': live })
  };

  if (!isValidElement(children)) {
    return children;
  }

  return (
    <>
      <span id={labelId} className="sr-only">
        {label}
        {required && ' (required)'}
      </span>
      {description && (
        <span id={descId} className="sr-only">
          {description}
        </span>
      )}
      {cloneElement(children, {
        ...(children.props as Record<string, any>),
        ...ariaProps
      })}
    </>
  );
}

// Complex UI Component Labels

// Data Table with ARIA Labels
interface DataTableAriaProps {
  children: ReactNode;
  caption: string;
  sortable?: boolean;
  filterable?: boolean;
  rowCount?: number;
  selectedRows?: number;
}

export function DataTableAria({
  children,
  caption,
  sortable = false,
  filterable = false,
  rowCount,
  selectedRows
}: DataTableAriaProps) {
  const { generateId } = useAriaLabels();
  const captionId = generateId('table-caption');
  const statusId = generateId('table-status');

  return (
    <div role="region" aria-labelledby={captionId}>
      <div id={captionId} className="sr-only">
        {caption}
        {sortable && ' - Sortable table'}
        {filterable && ' - Filterable table'}
      </div>
      
      {(rowCount !== undefined || selectedRows !== undefined) && (
        <div
          id={statusId}
          className="sr-only"
          aria-live="polite"
          aria-atomic="true"
        >
          {rowCount !== undefined && `${rowCount} rows total`}
          {selectedRows !== undefined && `, ${selectedRows} selected`}
        </div>
      )}
      
      <div
        role="table"
        aria-labelledby={captionId}
        aria-describedby={statusId}
        aria-rowcount={rowCount}
      >
        {children}
      </div>
    </div>
  );
}

// Chart with ARIA Labels
interface ChartAriaProps {
  children: ReactNode;
  title: string;
  description: string;
  dataPoints?: number;
  chartType: 'line' | 'bar' | 'pie' | 'scatter' | 'area';
  hasInteraction?: boolean;
}

export function ChartAria({
  children,
  title,
  description,
  dataPoints,
  chartType,
  hasInteraction = false
}: ChartAriaProps) {
  const { generateId } = useAriaLabels();
  const titleId = generateId('chart-title');
  const descId = generateId('chart-desc');

  return (
    <div
      role="img"
      aria-labelledby={titleId}
      aria-describedby={descId}
      tabIndex={hasInteraction ? 0 : undefined}
    >
      <div id={titleId} className="sr-only">
        {title} - {chartType} chart
      </div>
      <div id={descId} className="sr-only">
        {description}
        {dataPoints && ` Contains ${dataPoints} data points.`}
        {hasInteraction && ' Use arrow keys to navigate chart elements.'}
      </div>
      {children}
    </div>
  );
}

// Agent Status with ARIA Labels
interface AgentStatusAriaProps {
  children: ReactNode;
  agentName: string;
  status: 'active' | 'idle' | 'error' | 'loading';
  taskCount?: number;
  lastActivity?: string;
}

export function AgentStatusAria({
  children,
  agentName,
  status,
  taskCount,
  lastActivity
}: AgentStatusAriaProps) {
  const { generateId } = useAriaLabels();
  const labelId = generateId('agent-label');
  const statusId = generateId('agent-status');

  const statusText = {
    active: 'Currently active',
    idle: 'Idle, waiting for tasks',
    error: 'Error state, requires attention',
    loading: 'Processing tasks'
  }[status];

  return (
    <div
      role="status"
      aria-labelledby={labelId}
      aria-describedby={statusId}
      aria-live={status === 'error' ? 'assertive' : 'polite'}
    >
      <div id={labelId} className="sr-only">
        {agentName} Agent
      </div>
      <div id={statusId} className="sr-only">
        {statusText}
        {taskCount !== undefined && `. ${taskCount} tasks in queue`}
        {lastActivity && `. Last activity: ${lastActivity}`}
      </div>
      {children}
    </div>
  );
}

// Modal Dialog with ARIA Labels
interface ModalAriaProps {
  children: ReactNode;
  title: string;
  description?: string;
  isOpen: boolean;
  onClose: () => void;
  size?: 'sm' | 'md' | 'lg' | 'xl';
}

export function ModalAria({
  children,
  title,
  description,
  isOpen,
  onClose,
  size = 'md'
}: ModalAriaProps) {
  const { generateId } = useAriaLabels();
  const titleId = generateId('modal-title');
  const descId = description ? generateId('modal-desc') : undefined;

  React.useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby={titleId}
      aria-describedby={descId}
      className="fixed inset-0 z-50 flex items-center justify-center"
    >
      <div
        className="fixed inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
        aria-hidden="true"
      />
      <div
        className={`relative bg-white dark:bg-gray-800 rounded-lg shadow-xl max-h-[90vh] overflow-auto ${
          size === 'sm' ? 'max-w-sm' :
          size === 'md' ? 'max-w-md' :
          size === 'lg' ? 'max-w-lg' :
          'max-w-xl'
        } w-full mx-4`}
      >
        <div id={titleId} className="sr-only">
          {title}
        </div>
        {description && (
          <div id={descId} className="sr-only">
            {description}
          </div>
        )}
        {children}
      </div>
    </div>
  );
}

// Navigation with ARIA Labels
interface NavigationAriaProps {
  children: ReactNode;
  label: string;
  currentPage?: string;
  totalPages?: number;
}

export function NavigationAria({
  children,
  label,
  currentPage,
  totalPages
}: NavigationAriaProps) {
  const { generateId } = useAriaLabels();
  const navId = generateId('nav-label');

  return (
    <nav
      role="navigation"
      aria-labelledby={navId}
      aria-current={currentPage ? 'page' : undefined}
    >
      <div id={navId} className="sr-only">
        {label}
        {currentPage && totalPages && ` - Page ${currentPage} of ${totalPages}`}
      </div>
      {children}
    </nav>
  );
}

// Form Field with Enhanced ARIA
interface FormFieldAriaProps {
  children: ReactElement;
  label: string;
  error?: string;
  hint?: string;
  required?: boolean;
}

export function FormFieldAria({
  children,
  label,
  error,
  hint,
  required = false
}: FormFieldAriaProps) {
  const { generateId } = useAriaLabels();
  const labelId = generateId('field-label');
  const errorId = error ? generateId('field-error') : undefined;
  const hintId = hint ? generateId('field-hint') : undefined;

  const describedBy = [errorId, hintId].filter(Boolean).join(' ');

  if (!isValidElement(children)) {
    return children;
  }

  const childProps = children.props as Record<string, any>;

  return (
    <div className="space-y-1">
      <label
        id={labelId}
        htmlFor={childProps.id}
        className="block text-sm font-medium text-gray-700 dark:text-gray-300"
      >
        {label}
        {required && <span className="text-red-500 ml-1" aria-label="required">*</span>}
      </label>
      
      {hint && (
        <div id={hintId} className="text-xs text-gray-500 dark:text-gray-400">
          {hint}
        </div>
      )}
      
      {cloneElement(children, {
        ...childProps,
        'aria-labelledby': labelId,
        'aria-describedby': describedBy || undefined,
        'aria-required': required,
        'aria-invalid': !!error
      })}
      
      {error && (
        <div
          id={errorId}
          role="alert"
          className="text-xs text-red-600 dark:text-red-400"
        >
          {error}
        </div>
      )}
    </div>
  );
}
