/**
 * Accessibility Hook for 3D Visualizations
 * Week 19 Day 5 - ARIA support, keyboard nav, reduced motion
 *
 * Features:
 * - ARIA labels for canvas elements
 * - Keyboard navigation for camera controls
 * - prefers-reduced-motion detection and handling
 * - Screen reader announcements for 3D state changes
 */

'use client';

import { useEffect, useState, useCallback } from 'react';

export interface Accessibility3DConfig {
  /** ARIA label for the canvas element */
  ariaLabel: string;

  /** ARIA description providing context */
  ariaDescription?: string;

  /** Current state to announce to screen readers */
  currentState?: string;

  /** Enable keyboard navigation */
  enableKeyboardNav?: boolean;

  /** Respect prefers-reduced-motion */
  respectReducedMotion?: boolean;
}

export interface Accessibility3DResult {
  /** Props to spread onto Canvas element */
  canvasProps: {
    'aria-label': string;
    'aria-describedby'?: string;
    role: string;
    tabIndex: number;
  };

  /** Whether user prefers reduced motion */
  prefersReducedMotion: boolean;

  /** Function to announce state changes to screen readers */
  announceToScreenReader: (message: string) => void;

  /** Keyboard event handlers */
  handleKeyDown: (e: React.KeyboardEvent) => void;
}

/**
 * Hook for 3D visualization accessibility
 */
export function useAccessibility3D(
  config: Accessibility3DConfig
): Accessibility3DResult {
  const {
    ariaLabel,
    ariaDescription,
    currentState,
    enableKeyboardNav = true,
    respectReducedMotion = true,
  } = config;

  // Detect prefers-reduced-motion
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);

  useEffect(() => {
    if (!respectReducedMotion) return;

    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setPrefersReducedMotion(mediaQuery.matches);

    const handler = (e: MediaQueryListEvent) => {
      setPrefersReducedMotion(e.matches);
    };

    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, [respectReducedMotion]);

  // Screen reader announcements
  const announceToScreenReader = useCallback((message: string) => {
    const liveRegion = document.getElementById('a11y-live-region');
    if (liveRegion) {
      liveRegion.textContent = message;

      // Clear after 1 second to allow re-announcement of same message
      setTimeout(() => {
        liveRegion.textContent = '';
      }, 1000);
    }
  }, []);

  // Announce current state changes
  useEffect(() => {
    if (currentState) {
      announceToScreenReader(currentState);
    }
  }, [currentState, announceToScreenReader]);

  // Keyboard navigation handler
  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (!enableKeyboardNav) return;

    // These controls work with OrbitControls
    // Arrow keys: rotate camera
    // +/-: zoom in/out
    // R: reset camera

    switch (e.key) {
      case 'r':
      case 'R':
        announceToScreenReader('Camera reset to default position');
        // OrbitControls will handle the actual reset via its own reset() method
        break;

      case 'ArrowLeft':
      case 'ArrowRight':
      case 'ArrowUp':
      case 'ArrowDown':
        announceToScreenReader('Camera rotating');
        break;

      case '+':
      case '=':
        announceToScreenReader('Zooming in');
        break;

      case '-':
      case '_':
        announceToScreenReader('Zooming out');
        break;

      case '?':
        announceToScreenReader(
          'Keyboard shortcuts: Arrow keys to rotate, plus and minus to zoom, R to reset camera'
        );
        break;
    }
  }, [enableKeyboardNav, announceToScreenReader]);

  // Generate unique ID for aria-describedby
  const descriptionId = ariaDescription
    ? `canvas-desc-${ariaLabel.replace(/\s+/g, '-').toLowerCase()}`
    : undefined;

  return {
    canvasProps: {
      'aria-label': ariaLabel,
      'aria-describedby': descriptionId,
      role: 'img', // Canvas acts as an image for screen readers
      tabIndex: 0, // Make focusable for keyboard navigation
    },
    prefersReducedMotion,
    announceToScreenReader,
    handleKeyDown,
  };
}

/**
 * Global live region component for screen reader announcements
 * Add this once in your root layout
 */
export function AccessibilityLiveRegion() {
  return (
    <div
      id="a11y-live-region"
      aria-live="polite"
      aria-atomic="true"
      className="sr-only"
    />
  );
}
