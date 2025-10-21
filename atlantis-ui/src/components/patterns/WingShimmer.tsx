'use client';

/**
 * WingShimmer - Gradient shimmer effect for bee wings
 *
 * Creates an animated gradient that simulates the iridescent
 * shimmer of bee wings. Can be applied to SVG elements or
 * used as background gradients.
 *
 * Usage:
 * <WingShimmer id="wing-shimmer" />
 * <rect fill="url(#wing-shimmer)" />
 */

interface WingShimmerProps {
  id?: string;
  animate?: boolean;
}

export function WingShimmer({
  id = 'wing-shimmer',
  animate = true,
}: WingShimmerProps) {
  return (
    <svg width="0" height="0" style={{ position: 'absolute' }}>
      <defs>
        <linearGradient id={id} x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#FFFFFF" stopOpacity="0.8">
            {animate && (
              <animate
                attributeName="stopOpacity"
                values="0.8;0.4;0.8"
                dur="2s"
                repeatCount="indefinite"
              />
            )}
          </stop>
          <stop offset="50%" stopColor="#FFB300" stopOpacity="0.4">
            {animate && (
              <animate
                attributeName="stopOpacity"
                values="0.4;0.8;0.4"
                dur="2s"
                repeatCount="indefinite"
              />
            )}
          </stop>
          <stop offset="100%" stopColor="#FFFFFF" stopOpacity="0.8">
            {animate && (
              <animate
                attributeName="stopOpacity"
                values="0.8;0.4;0.8"
                dur="2s"
                repeatCount="indefinite"
              />
            )}
          </stop>
        </linearGradient>
      </defs>
    </svg>
  );
}
