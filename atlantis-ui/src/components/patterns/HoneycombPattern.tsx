'use client';

/**
 * HoneycombPattern - SVG pattern for bee-themed backgrounds
 *
 * Creates a repeating hexagonal honeycomb pattern that can be used
 * as backgrounds, fills, or overlays throughout the Atlantis UI.
 *
 * Usage:
 * <HoneycombPattern id="honeycomb" color="#FFB300" opacity={0.2} />
 * <div style={{ backgroundImage: 'url(#honeycomb)' }}>Content</div>
 */

interface HoneycombPatternProps {
  id?: string;
  color?: string;
  opacity?: number;
  strokeWidth?: number;
}

export function HoneycombPattern({
  id = 'honeycomb',
  color = '#FFB300',
  opacity = 0.2,
  strokeWidth = 2,
}: HoneycombPatternProps) {
  return (
    <svg width="0" height="0" style={{ position: 'absolute' }}>
      <defs>
        <pattern
          id={id}
          x="0"
          y="0"
          width="56"
          height="100"
          patternUnits="userSpaceOnUse"
        >
          {/* Main hexagon */}
          <path
            d="M28 66L0 50L0 18L28 2L56 18L56 50L28 66"
            fill="none"
            stroke={color}
            strokeWidth={strokeWidth}
            opacity={opacity}
          />
          {/* Extended hexagon for seamless tiling */}
          <path
            d="M28 66L28 98"
            fill="none"
            stroke={color}
            strokeWidth={strokeWidth}
            opacity={opacity}
          />
        </pattern>
      </defs>
    </svg>
  );
}
