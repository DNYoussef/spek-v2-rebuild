'use client';

import { useRef, useMemo, useState, useEffect } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

/**
 * HoneycombCell3D - 3D hexagonal cell with honey filling
 *
 * Represents tasks as honeycomb cells that fill with honey
 * as they progress from pending → in-progress → complete.
 *
 * Props:
 * - position: [x, y, z] position in 3D space
 * - state: 'empty' | 'filling' | 'full'
 * - fillProgress: 0-1 (for 'filling' state)
 * - glow: Enable glow effect for completed cells
 */

interface HoneycombCell3DProps {
  position?: [number, number, number];
  state?: 'empty' | 'filling' | 'full';
  fillProgress?: number;
  glow?: boolean;
  onClick?: () => void;
}

export function HoneycombCell3D({
  position = [0, 0, 0],
  state = 'empty',
  fillProgress = 0,
  glow = true,
  onClick,
}: HoneycombCell3DProps) {
  const cellRef = useRef<THREE.Mesh>(null);
  const honeyRef = useRef<THREE.Mesh>(null);
  const [animatedFill, setAnimatedFill] = useState(fillProgress);

  // Animate fill progress
  useEffect(() => {
    const start = animatedFill;
    const end = state === 'full' ? 1 : fillProgress;
    const duration = 2500; // 2.5 seconds
    const startTime = Date.now();

    const animate = () => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / duration, 1);
      // Ease-out cubic for honey pour effect
      const eased = 1 - Math.pow(1 - progress, 3);
      setAnimatedFill(start + (end - start) * eased);

      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };

    if (Math.abs(end - start) > 0.01) {
      animate();
    }
  }, [state, fillProgress]);

  // Create hexagon shape
  const hexagonShape = useMemo(() => {
    const shape = new THREE.Shape();
    const radius = 0.5;
    for (let i = 0; i < 6; i++) {
      const angle = (Math.PI / 3) * i;
      const x = Math.cos(angle) * radius;
      const y = Math.sin(angle) * radius;
      if (i === 0) {
        shape.moveTo(x, y);
      } else {
        shape.lineTo(x, y);
      }
    }
    shape.closePath();
    return shape;
  }, []);

  // Cell material (outline)
  const cellMaterial = useMemo(() => {
    const baseColor =
      state === 'full' ? '#FFB300' : state === 'filling' ? '#F39C12' : '#8B4513';

    return new THREE.MeshStandardMaterial({
      color: new THREE.Color(baseColor),
      metalness: 0.4,
      roughness: 0.6,
      transparent: state === 'empty',
      opacity: state === 'empty' ? 0.3 : 1.0,
      emissive: state === 'full' && glow ? new THREE.Color('#FFB300') : undefined,
      emissiveIntensity: state === 'full' && glow ? 0.3 : 0,
    });
  }, [state, glow]);

  // Honey material (filling)
  const honeyMaterial = useMemo(() => {
    return new THREE.MeshPhysicalMaterial({
      color: new THREE.Color('#FFB300'),
      metalness: 0.2,
      roughness: 0.3,
      transparent: true,
      opacity: 0.8,
      clearcoat: 1.0,
      clearcoatRoughness: 0.2,
    });
  }, []);

  // Glow animation for full cells
  useFrame((frameState) => {
    if (!cellRef.current || !glow || state !== 'full') return;

    const time = frameState.clock.getElapsedTime();
    const intensity = 0.3 + Math.sin(time * 2) * 0.1;
    (cellRef.current.material as THREE.MeshStandardMaterial).emissiveIntensity =
      intensity;
  });

  const cellDepth = 0.3;
  const honeyHeight = animatedFill * cellDepth;

  return (
    <group position={position} onClick={onClick}>
      {/* Cell outline (hexagonal prism) */}
      <mesh ref={cellRef}>
        <extrudeGeometry
          args={[
            hexagonShape,
            { depth: cellDepth, bevelEnabled: false },
          ]}
        />
        <meshStandardMaterial {...cellMaterial} />
      </mesh>

      {/* Honey filling (only visible when filling or full) */}
      {(state === 'filling' || state === 'full') && (
        <mesh
          ref={honeyRef}
          position={[0, 0, -(cellDepth - honeyHeight) / 2]}
        >
          <extrudeGeometry
            args={[
              hexagonShape,
              { depth: honeyHeight, bevelEnabled: false },
            ]}
          />
          <meshPhysicalMaterial {...honeyMaterial} />
        </mesh>
      )}

      {/* Cell edges (wireframe for definition) */}
      <lineSegments>
        <edgesGeometry
          args={[
            new THREE.ExtrudeGeometry(hexagonShape, {
              depth: cellDepth,
              bevelEnabled: false,
            }),
          ]}
        />
        <lineBasicMaterial color="#654321" linewidth={2} />
      </lineSegments>
    </group>
  );
}

/**
 * Helper function to create hexagonal grid positions
 */
export function createHexGrid(
  rows: number,
  cols: number,
  spacing: number = 1.1
): [number, number, number][] {
  const positions: [number, number, number][] = [];
  const hexWidth = spacing;
  const hexHeight = spacing * 0.866; // sqrt(3)/2

  for (let row = 0; row < rows; row++) {
    for (let col = 0; col < cols; col++) {
      const x = col * hexWidth + (row % 2 === 1 ? hexWidth / 2 : 0);
      const y = row * hexHeight;
      positions.push([x, y, 0]);
    }
  }

  return positions;
}
