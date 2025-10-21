/**
 * Card Component
 *
 * Reusable card container with variants.
 *
 * Version: 8.0.0
 * Week: 7 Day 4
 */

import { HTMLAttributes, ReactNode } from 'react';

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'elevated' | 'bordered';
  padding?: 'none' | 'sm' | 'md' | 'lg';
  children: ReactNode;
}

export function Card({
  variant = 'default',
  padding = 'md',
  className = '',
  children,
  ...props
}: CardProps) {
  const variantClasses = {
    default: 'bg-white rounded-lg',
    elevated: 'bg-white rounded-lg shadow-lg',
    bordered: 'bg-white rounded-lg border border-gray-200'
  };

  const paddingClasses = {
    none: '',
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8'
  };

  const classes = `${variantClasses[variant]} ${paddingClasses[padding]} ${className}`;

  return (
    <div className={classes} {...props}>
      {children}
    </div>
  );
}
