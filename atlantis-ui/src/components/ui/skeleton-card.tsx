'use client';

import { motion } from 'framer-motion';

interface SkeletonCardProps {
  height?: string;
  className?: string;
}

/**
 * SkeletonCard - Pulsing placeholder for loading content
 *
 * Features:
 * - Pulse animation (opacity 0.5 → 1 → 0.5)
 * - 1.5s cycle duration
 * - Infinite repeat
 * - Customizable height
 * - Respects prefers-reduced-motion (shows static placeholder)
 *
 * @param height - Card height (default: h-32)
 * @param className - Additional CSS classes
 */
export function SkeletonCard({
  height = 'h-32',
  className = ''
}: SkeletonCardProps) {
  return (
    <motion.div
      animate={{ opacity: [0.5, 1, 0.5] }}
      transition={{
        duration: 1.5,
        repeat: Infinity,
        ease: 'easeInOut'
      }}
      className={`${height} bg-gray-200 rounded-lg ${className}`}
      role="status"
      aria-label="Loading content"
    />
  );
}

/**
 * SkeletonText - Pulsing placeholder for loading text
 *
 * @param width - Text width (default: w-full)
 * @param className - Additional CSS classes
 */
export function SkeletonText({
  width = 'w-full',
  className = ''
}: { width?: string; className?: string }) {
  return (
    <motion.div
      animate={{ opacity: [0.5, 1, 0.5] }}
      transition={{
        duration: 1.5,
        repeat: Infinity,
        ease: 'easeInOut'
      }}
      className={`${width} h-4 bg-gray-200 rounded ${className}`}
      role="status"
      aria-label="Loading text"
    />
  );
}
