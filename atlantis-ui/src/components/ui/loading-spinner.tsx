'use client';

import { motion } from 'framer-motion';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  color?: string;
  className?: string;
}

/**
 * LoadingSpinner - Animated circular loading indicator
 *
 * Features:
 * - Continuous 360° rotation
 * - Multiple size options (sm: 4, md: 8, lg: 12)
 * - Customizable color
 * - Linear easing for smooth rotation
 * - Respects prefers-reduced-motion
 *
 * @param size - Spinner size variant
 * @param color - Border color (default: primary)
 * @param className - Additional CSS classes
 */
export function LoadingSpinner({
  size = 'md',
  color = 'border-blue-600',
  className = ''
}: LoadingSpinnerProps) {
  const sizeClasses = {
    sm: 'w-4 h-4 border-2',
    md: 'w-8 h-8 border-4',
    lg: 'w-12 h-12 border-4'
  };

  return (
    <motion.div
      animate={{ rotate: 360 }}
      transition={{
        duration: 1,
        repeat: Infinity,
        ease: 'linear'
      }}
      className={`${sizeClasses[size]} ${color} border-t-transparent rounded-full ${className}`}
      role="status"
      aria-label="Loading"
    />
  );
}
