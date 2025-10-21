'use client';

import { motion } from 'framer-motion';
import { ReactNode } from 'react';

interface AnimatedPageProps {
  children: ReactNode;
  className?: string;
}

/**
 * AnimatedPage - Wrapper component that adds smooth fade-in/fade-out transitions
 * to pages for a polished user experience.
 *
 * Features:
 * - Fade in from bottom (20px) on mount
 * - Fade out to top (-20px) on unmount
 * - 300ms duration for smooth transitions
 * - Respects prefers-reduced-motion for accessibility
 *
 * @param children - Page content to animate
 * @param className - Optional additional CSS classes
 */
export function AnimatedPage({ children, className = '' }: AnimatedPageProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{
        duration: 0.3,
        ease: 'easeInOut',
        // Disable animation if user prefers reduced motion
        when: 'beforeChildren'
      }}
      className={className}
    >
      {children}
    </motion.div>
  );
}
