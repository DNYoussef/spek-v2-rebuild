'use client';

import { motion } from 'framer-motion';
import { ReactNode, ButtonHTMLAttributes } from 'react';

// Omit conflicting props to avoid conflicts with framer-motion's event handlers
interface AnimatedButtonProps extends Omit<ButtonHTMLAttributes<HTMLButtonElement>, 'onAnimationStart' | 'onDrag' | 'onDragStart' | 'onDragEnd'> {
  children: ReactNode;
  variant?: 'default' | 'primary' | 'secondary' | 'outline' | 'ghost';
}

/**
 * AnimatedButton - Interactive button with hover and press animations
 *
 * Features:
 * - Scale up 5% on hover (1.05x)
 * - Scale down 5% on press (0.95x)
 * - Spring physics for natural feel
 * - Respects prefers-reduced-motion
 * - Maintains accessibility (keyboard, screen readers)
 *
 * @param children - Button content
 * @param variant - Visual style variant
 * @param className - Additional CSS classes
 * @param props - Standard button HTML attributes
 */
export function AnimatedButton({
  children,
  variant = 'default',
  className = '',
  ...props
}: AnimatedButtonProps) {
  const baseClasses = 'px-4 py-2 rounded-lg font-medium transition-colors';

  const variantClasses = {
    default: 'bg-gray-200 hover:bg-gray-300 text-gray-900',
    primary: 'bg-blue-600 hover:bg-blue-700 text-white',
    secondary: 'bg-purple-600 hover:bg-purple-700 text-white',
    outline: 'border-2 border-gray-300 hover:border-gray-400 bg-transparent',
    ghost: 'hover:bg-gray-100 bg-transparent'
  };

  return (
    <motion.button
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      transition={{
        type: 'spring',
        stiffness: 400,
        damping: 17
      }}
      className={`${baseClasses} ${variantClasses[variant]} ${className}`}
      type="button"
      {...props}
    >
      {children}
    </motion.button>
  );
}
