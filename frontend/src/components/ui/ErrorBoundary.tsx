'use client';

import React from 'react';
import { AlertTriangle, RefreshCw, Home } from 'lucide-react';

interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
  errorInfo?: React.ErrorInfo;
}

interface ErrorBoundaryProps {
  children: React.ReactNode;
  fallback?: React.ComponentType<{ error: Error; retry: () => void }>;
}

class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    // Update state so the next render will show the fallback UI
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // Log the error to our logging service
    console.error('Error caught by ErrorBoundary:', error, errorInfo);
    
    this.setState({
      hasError: true,
      error,
      errorInfo
    });

    // In production, send to error reporting service
    if (process.env.NODE_ENV === 'production') {
      // TODO: Send to Sentry or other error tracking service
    }
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: undefined, errorInfo: undefined });
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        const FallbackComponent = this.props.fallback;
        return <FallbackComponent error={this.state.error!} retry={this.handleRetry} />;
      }

      return (
        <DefaultErrorFallback 
          error={this.state.error!} 
          retry={this.handleRetry}
          isDevelopment={process.env.NODE_ENV === 'development'}
        />
      );
    }

    return this.props.children;
  }
}

interface DefaultErrorFallbackProps {
  error: Error;
  retry: () => void;
  isDevelopment?: boolean;
}

const DefaultErrorFallback: React.FC<DefaultErrorFallbackProps> = ({ 
  error, 
  retry, 
  isDevelopment = false 
}) => {
  const goHome = () => {
    window.location.href = '/';
  };

  return (
    <div 
      className="min-h-screen flex items-center justify-center bg-gradient-to-br from-background via-background/90 to-primary/20"
      role="alert"
      aria-live="assertive"
    >
      <div className="card-glass p-8 max-w-lg w-full mx-4 text-center">
        <div className="flex justify-center mb-6">
          <div className="p-4 bg-accent-error/20 rounded-full">
            <AlertTriangle 
              className="w-12 h-12 text-accent-error" 
              aria-hidden="true"
            />
          </div>
        </div>
        
        <h1 className="text-2xl font-bold text-text-primary mb-4">
          Something went wrong
        </h1>
        
        <p className="text-text-secondary mb-6">
          We encountered an unexpected error. Please try refreshing the page or return to the home page.
        </p>

        {isDevelopment && (
          <details className="mb-6 text-left">
            <summary className="cursor-pointer text-accent-error font-medium mb-2">
              Error Details (Development Only)
            </summary>
            <div className="bg-surface/50 p-4 rounded border border-accent-error/20 text-sm font-mono">
              <p className="text-accent-error font-bold">{error.name}</p>
              <p className="text-text-secondary mb-2">{error.message}</p>
              {error.stack && (
                <pre className="text-xs text-text-tertiary overflow-auto">
                  {error.stack}
                </pre>
              )}
            </div>
          </details>
        )}

        <div className="flex gap-4 justify-center">
          <button
            onClick={retry}
            className="btn-primary flex items-center gap-2"
            aria-label="Retry the failed operation"
          >
            <RefreshCw className="w-4 h-4" aria-hidden="true" />
            Try Again
          </button>
          
          <button
            onClick={goHome}
            className="btn-secondary flex items-center gap-2"
            aria-label="Return to home page"
          >
            <Home className="w-4 h-4" aria-hidden="true" />
            Go Home
          </button>
        </div>
      </div>
    </div>
  );
};

// HOC for wrapping components with error boundary
export function withErrorBoundary<P extends object>(
  Component: React.ComponentType<P>,
  fallback?: React.ComponentType<{ error: Error; retry: () => void }>
) {
  const WrappedComponent = (props: P) => (
    <ErrorBoundary fallback={fallback}>
      <Component {...props} />
    </ErrorBoundary>
  );

  WrappedComponent.displayName = `withErrorBoundary(${Component.displayName || Component.name})`;
  
  return WrappedComponent;
}

export default ErrorBoundary;
