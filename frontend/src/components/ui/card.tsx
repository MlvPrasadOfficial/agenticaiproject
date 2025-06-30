'use client';

import React from 'react';
import { cn } from '@/lib/utils';

interface CardProps {
  readonly className?: string;
  readonly children: React.ReactNode;
}

export function Card({ className, children }: CardProps) {
  return (
    <div
      className={cn(
        'rounded-lg border bg-card text-card-foreground shadow-sm',
        className
      )}
    >
      {children}
    </div>
  );
}

interface CardHeaderProps {
  readonly className?: string;
  readonly children: React.ReactNode;
}

export function CardHeader({ className, children }: CardHeaderProps) {
  return (
    <div className={cn('flex flex-col space-y-1.5 p-6', className)}>
      {children}
    </div>
  );
}

interface CardTitleProps {
  readonly className?: string;
  readonly children: React.ReactNode;
  readonly as?: 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6';
}

export function CardTitle({ className, children, as: Component = 'h3' }: CardTitleProps) {
  return (
    <Component className={cn('text-2xl font-semibold leading-none tracking-tight', className)}>
      {children}
    </Component>
  );
}

interface CardDescriptionProps {
  readonly className?: string;
  readonly children: React.ReactNode;
}

export function CardDescription({ className, children }: CardDescriptionProps) {
  return (
    <p className={cn('text-sm text-muted-foreground', className)}>
      {children}
    </p>
  );
}

interface CardContentProps {
  readonly className?: string;
  readonly children: React.ReactNode;
}

export function CardContent({ className, children }: CardContentProps) {
  return (
    <div className={cn('p-6 pt-0', className)}>
      {children}
    </div>
  );
}

interface CardFooterProps {
  readonly className?: string;
  readonly children: React.ReactNode;
}

export function CardFooter({ className, children }: CardFooterProps) {
  return (
    <div className={cn('flex items-center p-6 pt-0', className)}>
      {children}
    </div>
  );
}
