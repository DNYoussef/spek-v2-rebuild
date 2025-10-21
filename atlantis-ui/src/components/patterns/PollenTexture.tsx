'use client';

/**
 * PollenTexture - Particle texture for pollen effects
 *
 * Creates a repeating pattern of small circles that simulate
 * pollen particles. Used for subtle background textures and
 * particle effects in bee-themed visualizations.
 *
 * Usage:
 * <PollenTexture id="pollen" size={2} density={8} />
 * <rect fill="url(#pollen)" />
 */

interface PollenTextureProps {
  id?: string;
  size?: number;
  density?: number;
  color?: string;
  opacity?: number;
}

export function PollenTexture({
  id = 'pollen',
  size = 2,
  density = 8,
  color = '#FFEF00',
  opacity = 0.3,
}: PollenTextureProps) {
  const patternSize = density * 2;

  return (
    <svg width="0" height="0" style={{ position: 'absolute' }}>
      <defs>
        <pattern
          id={id}
          x="0"
          y="0"
          width={patternSize}
          height={patternSize}
          patternUnits="userSpaceOnUse"
        >
          {/* Pollen particles at different positions */}
          <circle
            cx={density * 0.25}
            cy={density * 0.25}
            r={size}
            fill={color}
            opacity={opacity}
          />
          <circle
            cx={density * 0.75}
            cy={density * 0.75}
            r={size * 0.8}
            fill={color}
            opacity={opacity * 0.8}
          />
          <circle
            cx={density * 1.25}
            cy={density * 0.5}
            r={size * 0.6}
            fill={color}
            opacity={opacity * 0.6}
          />
          <circle
            cx={density * 0.5}
            cy={density * 1.25}
            r={size * 0.7}
            fill={color}
            opacity={opacity * 0.7}
          />
        </pattern>
      </defs>
    </svg>
  );
}
