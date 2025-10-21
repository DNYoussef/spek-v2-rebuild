/**
 * Camera Controls Component
 *
 * Provides orbit, pan, zoom controls for 3D scenes
 * Research-backed UX patterns for 3D navigation
 */

'use client';

import { OrbitControls } from '@react-three/drei';

interface CameraControlsProps {
  enableDamping?: boolean;
  dampingFactor?: number;
  minDistance?: number;
  maxDistance?: number;
  enablePan?: boolean;
  enableZoom?: boolean;
  enableRotate?: boolean;
}

export function CameraControls({
  enableDamping = true,
  dampingFactor = 0.05,
  minDistance = 10,
  maxDistance = 500,
  enablePan = true,
  enableZoom = true,
  enableRotate = true,
}: CameraControlsProps) {
  return (
    <OrbitControls
      enableDamping={enableDamping}
      dampingFactor={dampingFactor}
      minDistance={minDistance}
      maxDistance={maxDistance}
      enablePan={enablePan}
      enableZoom={enableZoom}
      enableRotate={enableRotate}
      // Smooth scrolling for zoom
      mouseButtons={{
        LEFT: 0,   // Rotate
        MIDDLE: 1, // Pan
        RIGHT: 2,  // Zoom (right-click)
      }}
    />
  );
}
