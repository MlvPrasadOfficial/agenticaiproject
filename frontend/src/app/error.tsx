'use client';

import React from 'react';
import { AlertTriangle, RefreshCw, Home } from 'lucide-react';

interface ErrorPageProps {
  error: Error & { digest?: string };
  reset: () => void;
}

export default function ErrorPage({ error, reset }: ErrorPageProps) {
  React.useEffect(() => {
    // Log the error to console and error reporting service
    console.error('Global error caught:', error);
    
    // In production, send to error tracking service
    if (process.env.NODE_ENV === 'production') {
      // TODO: Send to Sentry or other error tracking service
    }
  }, [error]);

  const goHome = () => {
    window.location.href = '/';
  };

  return (
    <html>
      <body>
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
              Application Error
            </h1>
            
            <p className="text-text-secondary mb-6">
              We encountered an unexpected error while loading the application. 
              Please try refreshing the page.
            </p>

            {process.env.NODE_ENV === 'development' && (
              <details className="mb-6 text-left">
                <summary className="cursor-pointer text-accent-error font-medium mb-2">
                  Error Details (Development Only)
                </summary>
                <div className="bg-surface/50 p-4 rounded border border-accent-error/20 text-sm font-mono">
                  <p className="text-accent-error font-bold">{error.name}</p>
                  <p className="text-text-secondary mb-2">{error.message}</p>
                  {error.digest && (
                    <p className="text-text-tertiary text-xs mb-2">
                      Error ID: {error.digest}
                    </p>
                  )}
                  {error.stack && (
                    <pre className="text-xs text-text-tertiary overflow-auto max-h-40">
                      {error.stack}
                    </pre>
                  )}
                </div>
              </details>
            )}

            <div className="flex gap-4 justify-center">
              <button
                onClick={reset}
                className="btn-primary flex items-center gap-2"
                aria-label="Reset the application and try again"
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
      </body>
    </html>
  );
}
