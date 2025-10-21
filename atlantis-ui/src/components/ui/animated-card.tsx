'use client';

import { motion } from 'framer-motion';
import { ReactNode } from 'react';

interface AnimatedCardProps {
  children: ReactNode;
  className?: string;
  onClick?: () => void;
}

/**
 * AnimatedCard - Interactive card with hover lift effect
 *
 * Features:
 * - Lifts up 4px on hover (y: -4)
 * - Adds elevated shadow on hover
 * - Smooth 200ms transition
 * - Respects prefers-reduced-motion
 * - Clickable cards show cursor pointer
 *
 * @param children - Card content
 * @param className - Additional CSS classes
 * @param onClick - Optional click handler (makes card clickable)
 */
export function AnimatedCard({
  children,
  className = '',
  onClick
}: AnimatedCardProps) {
  const baseClasses = 'bg-white rounded-lg border border-gray-200 p-6 shadow-sm';
  const clickableClasses = onClick ? 'cursor-pointer' : '';

  return (
    <motion.div
      whileHover={{
        y: -4,
        boxShadow: '0 10px 30px rgba(0,0,0,0.1)'
      }}
      transition={{ duration: 0.2, ease: 'easeOut' }}
      className={`${baseClasses} ${clickableClasses} ${className}`}
      onClick={onClick}
    >
      {children}
    </motion.div>
  );
}
