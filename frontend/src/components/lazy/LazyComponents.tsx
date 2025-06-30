'use client';

import React, { lazy, Suspense } from 'react';
import { Loader2 } from 'lucide-react';

// Lazy loaded components for code splitting
const LazyDataPreview = lazy(() => import('@/components/DataPreview'));
const LazyAgentList = lazy(() => import('@/components/AgentList'));
const LazyModernDashboard = lazy(() => import('@/components/ModernDashboard'));

// Loading component
const ComponentLoader = ({ name }: { name: string }) => (
  <div className="flex items-center justify-center p-8 card-glass">
    <div className="flex items-center gap-3 text-text-secondary">
      <Loader2 className="w-5 h-5 animate-spin" />
      <span>Loading {name}...</span>
    </div>
  </div>
);

// HOC for lazy loading with error boundaries
function withLazyLoading<P extends object>(
  LazyComponent: React.LazyExoticComponent<React.ComponentType<P>>,
  name: string
) {
  return function LazyWrapper(props: P) {
    return (
      <Suspense fallback={<ComponentLoader name={name} />}>
        <LazyComponent {...props} />
      </Suspense>
    );
  };
}

// Export lazy components
export const LazyDataPreviewComponent = withLazyLoading(LazyDataPreview, 'Data Preview');
export const LazyAgentListComponent = withLazyLoading(LazyAgentList, 'Agent List');
export const LazyModernDashboardComponent = withLazyLoading(LazyModernDashboard, 'Dashboard');

// Performance monitoring HOC
export function withPerformanceMonitoring<P extends object>(
  Component: React.ComponentType<P>,
  componentName: string
) {
  return React.memo(function PerformanceWrapper(props: P) {
    React.useEffect(() => {
      const startTime = performance.now();
      
      return () => {
        const endTime = performance.now();
        const renderTime = endTime - startTime;
        
        // Log slow renders in development
        if (process.env.NODE_ENV === 'development' && renderTime > 100) {
          console.warn(`${componentName} took ${renderTime.toFixed(2)}ms to render`);
        }
        
        // Send to analytics in production
        if (process.env.NODE_ENV === 'production' && renderTime > 500) {
          console.warn(`Slow render detected: ${componentName} took ${renderTime.toFixed(2)}ms`);
        }
      };
    });

    return <Component {...props} />;
  });
}
