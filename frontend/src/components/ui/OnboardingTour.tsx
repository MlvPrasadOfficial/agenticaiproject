'use client';

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, ChevronLeft, ChevronRight, Check } from 'lucide-react';
import { useFocusTrap, useAnnouncement, LiveRegion } from '@/lib/accessibility';

interface OnboardingStep {
  id: string;
  title: string;
  content: string;
  target?: string; // CSS selector for element to highlight
  position?: 'top' | 'bottom' | 'left' | 'right';
  action?: {
    label: string;
    onClick: () => void;
  };
}

interface OnboardingProps {
  steps: OnboardingStep[];
  isOpen: boolean;
  onComplete: () => void;
  onSkip: () => void;
  showProgress?: boolean;
  allowSkip?: boolean;
}

export default function OnboardingTour({
  steps,
  isOpen,
  onComplete,
  onSkip,
  showProgress = true,
  allowSkip = true
}: OnboardingProps) {
  const [currentStep, setCurrentStep] = useState(0);
  const [highlightedElement, setHighlightedElement] = useState<HTMLElement | null>(null);
  const { announcement, announce } = useAnnouncement();
  const focusTrapRef = useFocusTrap(isOpen);

  useEffect(() => {
    if (!isOpen || !steps[currentStep]?.target) {
      setHighlightedElement(null);
      return;
    }

    const element = document.querySelector(steps[currentStep].target!) as HTMLElement;
    if (element) {
      setHighlightedElement(element);
      element.scrollIntoView({ behavior: 'smooth', block: 'center' });
      
      // Announce step change
      announce(`Step ${currentStep + 1} of ${steps.length}: ${steps[currentStep].title}`);
    }
  }, [currentStep, steps, isOpen, announce]);

  const nextStep = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      onComplete();
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    switch (e.key) {
      case 'ArrowRight':
        e.preventDefault();
        nextStep();
        break;
      case 'ArrowLeft':
        e.preventDefault();
        if (currentStep > 0) prevStep();
        break;
      case 'Escape':
        e.preventDefault();
        if (allowSkip) onSkip();
        break;
    }
  };

  if (!isOpen) return null;

  const currentStepData = steps[currentStep];
  const isLastStep = currentStep === steps.length - 1;

  return (
    <>
      {/* Overlay */}
      <div className="fixed inset-0 z-50">
        {/* Backdrop */}
        <div className="absolute inset-0 bg-black/60" />
        
        {/* Highlight overlay */}
        {highlightedElement && (
          <OnboardingHighlight element={highlightedElement} />
        )}
        
        {/* Tour card */}
        <AnimatePresence mode="wait">
          <motion.div
            key={currentStep}
            ref={focusTrapRef}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="absolute z-10"
            style={getCardPosition(highlightedElement, currentStepData.position)}
            onKeyDown={handleKeyDown}
            role="dialog"
            aria-labelledby="onboarding-title"
            aria-describedby="onboarding-content"
            aria-modal="true"
          >
            <div className="card-glass p-6 max-w-sm w-screen mx-4 shadow-2xl">
              {/* Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h2 
                    id="onboarding-title"
                    className="text-lg font-semibold text-text-primary mb-1"
                  >
                    {currentStepData.title}
                  </h2>
                  {showProgress && (
                    <p className="text-sm text-text-tertiary">
                      Step {currentStep + 1} of {steps.length}
                    </p>
                  )}
                </div>
                {allowSkip && (
                  <button
                    onClick={onSkip}
                    className="p-1 rounded hover:bg-surface transition-colors focus:ring-2 focus:ring-primary focus:ring-offset-1"
                    aria-label="Skip onboarding tour"
                  >
                    <X className="w-4 h-4 text-text-secondary" />
                  </button>
                )}
              </div>

              {/* Content */}
              <p 
                id="onboarding-content"
                className="text-sm text-text-secondary mb-6 leading-relaxed"
              >
                {currentStepData.content}
              </p>

              {/* Action button */}
              {currentStepData.action && (
                <button
                  onClick={currentStepData.action.onClick}
                  className="btn-secondary w-full mb-4 text-sm"
                >
                  {currentStepData.action.label}
                </button>
              )}

              {/* Progress bar */}
              {showProgress && (
                <div className="mb-4">
                  <div className="w-full bg-surface rounded-full h-2">
                    <div
                      className="bg-primary h-2 rounded-full transition-all duration-300"
                      style={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}
                      role="progressbar"
                      aria-valuenow={currentStep + 1}
                      aria-valuemin={1}
                      aria-valuemax={steps.length}
                      aria-label="Tour progress"
                    />
                  </div>
                </div>
              )}

              {/* Navigation */}
              <div className="flex items-center justify-between">
                <button
                  onClick={prevStep}
                  disabled={currentStep === 0}
                  className="btn-secondary px-4 py-2 text-sm disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                  aria-label="Previous step"
                >
                  <ChevronLeft className="w-4 h-4" />
                  Back
                </button>

                <div className="flex gap-1">
                  {steps.map((_, index) => (
                    <button
                      key={index}
                      onClick={() => setCurrentStep(index)}
                      className={`w-2 h-2 rounded-full transition-colors ${
                        index === currentStep ? 'bg-primary' : 'bg-surface'
                      }`}
                      aria-label={`Go to step ${index + 1}`}
                    />
                  ))}
                </div>

                <button
                  onClick={nextStep}
                  className="btn-primary px-4 py-2 text-sm flex items-center gap-2"
                  aria-label={isLastStep ? 'Complete tour' : 'Next step'}
                >
                  {isLastStep ? (
                    <>
                      <Check className="w-4 h-4" />
                      Done
                    </>
                  ) : (
                    <>
                      Next
                      <ChevronRight className="w-4 h-4" />
                    </>
                  )}
                </button>
              </div>
            </div>
          </motion.div>
        </AnimatePresence>
      </div>

      <LiveRegion announcement={announcement} />
    </>
  );
}

// Component to highlight the target element
function OnboardingHighlight({ element }: { element: HTMLElement }) {
  const [rect, setRect] = useState<DOMRect | null>(null);

  useEffect(() => {
    if (!element) return;

    const updateRect = () => {
      setRect(element.getBoundingClientRect());
    };

    updateRect();
    
    const resizeObserver = new ResizeObserver(updateRect);
    resizeObserver.observe(element);
    window.addEventListener('scroll', updateRect);
    window.addEventListener('resize', updateRect);

    return () => {
      resizeObserver.disconnect();
      window.removeEventListener('scroll', updateRect);
      window.removeEventListener('resize', updateRect);
    };
  }, [element]);

  if (!rect) return null;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="absolute border-2 border-primary rounded-lg shadow-lg pointer-events-none"
      style={{
        left: rect.left - 4,
        top: rect.top - 4,
        width: rect.width + 8,
        height: rect.height + 8,
        boxShadow: '0 0 0 9999px rgba(0, 0, 0, 0.5)',
      }}
    />
  );
}

// Helper function to position the tour card
function getCardPosition(
  element: HTMLElement | null,
  position: OnboardingStep['position'] = 'bottom'
): React.CSSProperties {
  if (!element) {
    return {
      top: '50%',
      left: '50%',
      transform: 'translate(-50%, -50%)',
    };
  }

  const rect = element.getBoundingClientRect();
  const offset = 20;

  switch (position) {
    case 'top':
      return {
        left: rect.left + rect.width / 2,
        bottom: window.innerHeight - rect.top + offset,
        transform: 'translateX(-50%)',
      };
    case 'bottom':
      return {
        left: rect.left + rect.width / 2,
        top: rect.bottom + offset,
        transform: 'translateX(-50%)',
      };
    case 'left':
      return {
        right: window.innerWidth - rect.left + offset,
        top: rect.top + rect.height / 2,
        transform: 'translateY(-50%)',
      };
    case 'right':
      return {
        left: rect.right + offset,
        top: rect.top + rect.height / 2,
        transform: 'translateY(-50%)',
      };
    default:
      return {
        left: rect.left + rect.width / 2,
        top: rect.bottom + offset,
        transform: 'translateX(-50%)',
      };
  }
}

// Hook for managing onboarding state
export function useOnboarding(key: string) {
  const [hasCompleted, setHasCompleted] = useState(false);
  const [isActive, setIsActive] = useState(false);

  useEffect(() => {
    const completed = localStorage.getItem(`onboarding-${key}`) === 'true';
    setHasCompleted(completed);
  }, [key]);

  const start = () => {
    if (!hasCompleted) {
      setIsActive(true);
    }
  };

  const complete = () => {
    localStorage.setItem(`onboarding-${key}`, 'true');
    setHasCompleted(true);
    setIsActive(false);
  };

  const skip = () => {
    setIsActive(false);
  };

  const reset = () => {
    localStorage.removeItem(`onboarding-${key}`);
    setHasCompleted(false);
  };

  return {
    hasCompleted,
    isActive,
    start,
    complete,
    skip,
    reset,
  };
}
