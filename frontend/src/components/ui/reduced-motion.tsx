'use client';

import React, { createContext, useContext, ReactNode, useEffect, useState } from 'react';

// Reduced Motion Context
interface ReducedMotionContextType {
  prefersReducedMotion: boolean;
  toggleReducedMotion: () => void;
  isMotionSafe: boolean;
  getMotionClass: (motion: string, reduced?: string) => string;
  getTransition: (duration?: string) => string;
  getAnimation: (animation: string, reducedAnimation?: string) => string;
}

const ReducedMotionContext = createContext<ReducedMotionContextType | null>(null);

// Provider Component
interface ReducedMotionProviderProps {
  readonly children: ReactNode;
}

export function ReducedMotionProvider({ children }: ReducedMotionProviderProps) {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);
  const [userPreference, setUserPreference] = useState<boolean | null>(null);

  // Detect system preference
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    
    // Set initial value
    if (userPreference === null) {
      setPrefersReducedMotion(mediaQuery.matches);
    }

    // Listen for changes
    const handleChange = (e: MediaQueryListEvent) => {
      if (userPreference === null) {
        setPrefersReducedMotion(e.matches);
      }
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, [userPreference]);

  // Load user preference from localStorage
  useEffect(() => {
    const savedPreference = localStorage.getItem('reduced-motion-preference');
    if (savedPreference !== null) {
      const preference = savedPreference === 'true';
      setUserPreference(preference);
      setPrefersReducedMotion(preference);
    }
  }, []);

  // Toggle user preference
  const toggleReducedMotion = () => {
    const newValue = !prefersReducedMotion;
    setPrefersReducedMotion(newValue);
    setUserPreference(newValue);
    localStorage.setItem('reduced-motion-preference', newValue.toString());
  };

  // Helper to determine if motion is safe
  const isMotionSafe = !prefersReducedMotion;

  // Get appropriate class based on motion preference
  const getMotionClass = (motion: string, reduced = '') => {
    return prefersReducedMotion ? reduced : motion;
  };

  // Get appropriate transition
  const getTransition = (duration = '200ms') => {
    return prefersReducedMotion ? 'none' : `all ${duration} ease-in-out`;
  };

  // Get appropriate animation
  const getAnimation = (animation: string, reducedAnimation = 'none') => {
    return prefersReducedMotion ? reducedAnimation : animation;
  };

  // Apply global CSS variables
  useEffect(() => {
    const root = document.documentElement;
    
    if (prefersReducedMotion) {
      root.style.setProperty('--motion-duration', '0ms');
      root.style.setProperty('--motion-scale', '1');
      root.style.setProperty('--motion-translate', '0px');
      root.style.setProperty('--motion-rotate', '0deg');
      root.style.setProperty('--motion-ease', 'linear');
    } else {
      root.style.setProperty('--motion-duration', '200ms');
      root.style.setProperty('--motion-scale', '1.05');
      root.style.setProperty('--motion-translate', '10px');
      root.style.setProperty('--motion-rotate', '3deg');
      root.style.setProperty('--motion-ease', 'ease-in-out');
    }
  }, [prefersReducedMotion]);

  // Memoize context value to prevent unnecessary re-renders
  const contextValue = React.useMemo(
    () => ({
      prefersReducedMotion,
      toggleReducedMotion,
      isMotionSafe,
      getMotionClass,
      getTransition,
      getAnimation
    }),
    [prefersReducedMotion, isMotionSafe]
  );

  return (
    <ReducedMotionContext.Provider value={contextValue}>
      {children}
    </ReducedMotionContext.Provider>
  );
}

// Hook to use Reduced Motion
export function useReducedMotion() {
  const context = useContext(ReducedMotionContext);
  if (!context) {
    throw new Error('useReducedMotion must be used within a ReducedMotionProvider');
  }
  return context;
}

// Animated Components with Reduced Motion Support

// Fade Component
interface FadeProps {
  readonly children: ReactNode;
  readonly show: boolean;
  readonly duration?: number;
  readonly className?: string;
}

export function Fade({ children, show, duration = 200, className = '' }: FadeProps) {
  const { getTransition, getAnimation } = useReducedMotion();
  
  const style: React.CSSProperties = {
    transition: getTransition(`${duration}ms`),
    opacity: show ? 1 : 0,
    animation: getAnimation(
      show ? `fadeIn ${duration}ms ease-in-out` : `fadeOut ${duration}ms ease-in-out`,
      'none'
    )
  };

  return (
    <div className={className} style={style}>
      {children}
    </div>
  );
}

// Slide Component
interface SlideProps {
  readonly children: ReactNode;
  readonly show: boolean;
  readonly direction: 'up' | 'down' | 'left' | 'right';
  readonly duration?: number;
  readonly distance?: number;
  readonly className?: string;
}

export function Slide({
  children,
  show,
  direction,
  duration = 200,
  distance = 20,
  className = ''
}: SlideProps) {
  const { getTransition, prefersReducedMotion } = useReducedMotion();
  
  const transforms = {
    up: `translateY(${show ? 0 : distance}px)`,
    down: `translateY(${show ? 0 : -distance}px)`,
    left: `translateX(${show ? 0 : distance}px)`,
    right: `translateX(${show ? 0 : -distance}px)`
  };

  const style: React.CSSProperties = {
    transition: getTransition(`${duration}ms`),
    transform: prefersReducedMotion ? 'none' : transforms[direction],
    opacity: show ? 1 : 0
  };

  return (
    <div className={className} style={style}>
      {children}
    </div>
  );
}

// Scale Component
interface ScaleProps {
  readonly children: ReactNode;
  readonly show: boolean;
  readonly scale?: number;
  readonly duration?: number;
  readonly className?: string;
}

export function Scale({
  children,
  show,
  scale = 0.95,
  duration = 200,
  className = ''
}: ScaleProps) {
  const { getTransition, prefersReducedMotion } = useReducedMotion();
  
  const scaleValue = show ? 1 : scale;
  const transform = prefersReducedMotion ? 'none' : `scale(${scaleValue})`;
  
  const style: React.CSSProperties = {
    transition: getTransition(`${duration}ms`),
    transform,
    opacity: show ? 1 : 0
  };

  return (
    <div className={className} style={style}>
      {children}
    </div>
  );
}

// Rotate Component
interface RotateProps {
  readonly children: ReactNode;
  readonly angle: number;
  readonly duration?: number;
  readonly className?: string;
}

export function Rotate({ children, angle, duration = 200, className = '' }: RotateProps) {
  const { getTransition, prefersReducedMotion } = useReducedMotion();
  
  const style: React.CSSProperties = {
    transition: getTransition(`${duration}ms`),
    transform: prefersReducedMotion ? 'none' : `rotate(${angle}deg)`
  };

  return (
    <div className={className} style={style}>
      {children}
    </div>
  );
}

// Bounce Component
interface BounceProps {
  readonly children: ReactNode;
  readonly active: boolean;
  readonly duration?: number;
  readonly intensity?: number;
  readonly className?: string;
}

export function Bounce({
  children,
  active,
  duration = 300,
  intensity = 0.1,
  className = ''
}: BounceProps) {
  const { getAnimation, prefersReducedMotion } = useReducedMotion();
  
  const style: React.CSSProperties = {
    animation: active ? getAnimation(
      `bounce ${duration}ms ease-in-out`,
      `pulseOpacity ${duration}ms ease-in-out`
    ) : 'none'
  };

  // Add CSS keyframes if not reduced motion
  useEffect(() => {
    if (!prefersReducedMotion && !document.getElementById('motion-keyframes')) {
      const style = document.createElement('style');
      style.id = 'motion-keyframes';
      style.textContent = `
        @keyframes bounce {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-${intensity * 10}px); }
        }
        @keyframes pulseOpacity {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.8; }
        }
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        @keyframes fadeOut {
          from { opacity: 1; }
          to { opacity: 0; }
        }
      `;
      document.head.appendChild(style);
    }
  }, [prefersReducedMotion, intensity]);

  return (
    <div className={className} style={style}>
      {children}
    </div>
  );
}

// Stagger Container for List Animations
interface StaggerProps {
  readonly children: ReactNode[];
  readonly show: boolean;
  readonly staggerDelay?: number;
  readonly baseDelay?: number;
  readonly className?: string;
}

export function Stagger({
  children,
  show,
  staggerDelay = 100,
  baseDelay = 0,
  className = ''
}: StaggerProps) {
  const { prefersReducedMotion } = useReducedMotion();

  return (
    <div className={className}>
      {children.map((child, index) => {
        const animationDelay = prefersReducedMotion ? '0ms' : `${baseDelay + index * staggerDelay}ms`;
        
        let animation = 'none';
        if (show) {
          animation = prefersReducedMotion ? 'none' : 'fadeIn 300ms ease-out forwards';
        }
        
        const childKey = React.isValidElement(child) && child.key 
          ? child.key 
          : `stagger-${Date.now()}-${index}`;
        
        return (
          <div
            key={childKey}
            style={{
              animationDelay,
              animation,
              opacity: show ? 1 : 0
            }}
          >
            {child}
          </div>
        );
      })}
    </div>
  );
}

// Motion-Safe Wrapper
interface MotionSafeProps {
  readonly children: ReactNode;
  readonly fallback?: ReactNode;
  readonly className?: string;
}

export function MotionSafe({ children, fallback, className = '' }: MotionSafeProps) {
  const { isMotionSafe } = useReducedMotion();
  
  return (
    <div className={className}>
      {isMotionSafe ? children : (fallback || children)}
    </div>
  );
}

// Parallax Component (disabled for reduced motion)
interface ParallaxProps {
  readonly children: ReactNode;
  readonly speed?: number;
  readonly className?: string;
}

export function Parallax({ children, speed = 0.5, className = '' }: ParallaxProps) {
  const { prefersReducedMotion } = useReducedMotion();
  const [offset, setOffset] = useState(0);

  useEffect(() => {
    if (prefersReducedMotion) return;

    const handleScroll = () => {
      setOffset(window.pageYOffset * speed);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [speed, prefersReducedMotion]);

  const style: React.CSSProperties = {
    transform: prefersReducedMotion ? 'none' : `translateY(${offset}px)`
  };

  return (
    <div className={className} style={style}>
      {children}
    </div>
  );
}

// Preferences Toggle Component
interface MotionToggleProps {
  readonly className?: string;
  readonly label?: string;
}

export function MotionToggle({ className = '', label = 'Reduce motion' }: MotionToggleProps) {
  const { prefersReducedMotion, toggleReducedMotion } = useReducedMotion();

  return (
    <div className={`flex items-center space-x-3 ${className}`}>
      <button
        onClick={toggleReducedMotion}
        className={`
          relative inline-flex h-6 w-11 items-center rounded-full transition-colors
          ${prefersReducedMotion 
            ? 'bg-blue-600' 
            : 'bg-gray-200 dark:bg-gray-700'
          }
        `}
        role="switch"
        aria-checked={prefersReducedMotion}
        aria-label={label}
      >
        <span
          className={`
            inline-block h-4 w-4 transform rounded-full bg-white transition-transform
            ${prefersReducedMotion ? 'translate-x-6' : 'translate-x-1'}
          `}
        />
      </button>
      <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
        {label}
      </span>
    </div>
  );
}
