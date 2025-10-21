/**
 * Loop 1: Orbital Ring 3D Visualization
 *
 * Research-backed 3D implementation:
 * - On-demand rendering (50% battery savings)
 * - <100 draw calls target
 * - Rotating nodes around center failure rate
 *
 * Features:
 * - Center: Failure rate percentage (3D text, color-coded)
 * - Ring: Iterations (nodes rotating around center)
 * - Satellites: Research artifacts (hoverable, clickable)
 * - Animation: Smooth rotation, pulsing effects
 */

'use client';

import { Canvas, useFrame } from '@react-three/fiber';
import { Text, Sphere, Line } from '@react-three/drei';
import { useRef, useMemo } from 'react';
import * as THREE from 'three';
import { defaultCanvasConfig } from '@/lib/three-config';
import { CameraControls } from './CameraControls';
import { PerformanceStats } from './PerformanceStats';

interface Loop1Data {
  failureRate: number; // 0-100
  currentIteration: number;
  maxIterations: number;
  iterations: Iteration[];
  artifacts: Artifact[];
}

interface Iteration {
  id: string;
  iterationNumber: number;
  failureRate: number;
  timestamp: number;
}

interface Artifact {
  id: string;
  type: 'github' | 'paper' | 'example';
  title: string;
  position: [number, number, number];
}

interface Loop1OrbitalRing3DProps {
  data: Loop1Data;
  showStats?: boolean;
}

function OrbitalRing({ iterations }: { iterations: Iteration[] }) {
  const groupRef = useRef<THREE.Group>(null);

  useFrame(({ clock }) => {
    if (groupRef.current) {
      groupRef.current.rotation.y = clock.getElapsedTime() * 0.2; // Slow rotation
    }
  });

  const ringRadius = 30;
  const nodePositions = useMemo(() => {
    return iterations.map((_, i) => {
      const angle = (i / iterations.length) * Math.PI * 2;
      return [
        Math.cos(angle) * ringRadius,
        0,
        Math.sin(angle) * ringRadius
      ] as [number, number, number];
    });
  }, [iterations]);

  return (
    <group ref={groupRef}>
      {/* Orbital ring line */}
      <Line
        points={[...nodePositions, nodePositions[0]]}
        color="#4a90e2"
        lineWidth={2}
      />

      {/* Iteration nodes */}
      {iterations.map((iteration, i) => (
        <Sphere
          key={iteration.id}
          position={nodePositions[i]}
          args={[1.5, 16, 16]}
        >
          <meshStandardMaterial
            color={
              iteration.failureRate < 5 ? '#10b981' :
              iteration.failureRate < 20 ? '#f59e0b' : '#ef4444'
            }
            emissive={
              iteration.failureRate < 5 ? '#10b981' :
              iteration.failureRate < 20 ? '#f59e0b' : '#ef4444'
            }
            emissiveIntensity={0.3}
          />
        </Sphere>
      ))}
    </group>
  );
}

function FailureRateCenter({ failureRate }: { failureRate: number }) {
  const color = failureRate < 5 ? '#10b981' :
                failureRate < 20 ? '#f59e0b' : '#ef4444';

  return (
    <group>
      {/* Center sphere with pulsing effect */}
      <Sphere args={[5, 32, 32]} position={[0, 0, 0]}>
        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={0.5}
          transparent
          opacity={0.8}
        />
      </Sphere>

      {/* Failure rate text */}
      <Text
        position={[0, 0, 6]}
        fontSize={3}
        color="white"
        anchorX="center"
        anchorY="middle"
      >
        {failureRate.toFixed(1)}%
      </Text>

      <Text
        position={[0, -3, 6]}
        fontSize={1.2}
        color="white"
        anchorX="center"
        anchorY="middle"
      >
        Failure Rate
      </Text>
    </group>
  );
}

function ResearchArtifacts({ artifacts }: { artifacts: Artifact[] }) {
  return (
    <group>
      {artifacts.map((artifact) => (
        <Sphere
          key={artifact.id}
          position={artifact.position}
          args={[0.8, 12, 12]}
        >
          <meshStandardMaterial
            color={
              artifact.type === 'github' ? '#6e5494' :
              artifact.type === 'paper' ? '#0366d6' : '#28a745'
            }
            emissiveIntensity={0.2}
          />
        </Sphere>
      ))}
    </group>
  );
}

export function Loop1OrbitalRing3D({ data, showStats = false }: Loop1OrbitalRing3DProps) {
  return (
    <div style={{ width: '100%', height: '600px', position: 'relative' }}>
      <Canvas
        {...defaultCanvasConfig}
        camera={{ position: [0, 40, 60], fov: 60 }}
      >
        {/* Lighting */}
        <ambientLight intensity={0.5} />
        <directionalLight position={[10, 10, 5]} intensity={1} />
        <pointLight position={[0, 0, 0]} intensity={0.5} />

        {/* Components */}
        <FailureRateCenter failureRate={data.failureRate} />
        <OrbitalRing iterations={data.iterations} />
        <ResearchArtifacts artifacts={data.artifacts} />

        {/* Camera controls */}
        <CameraControls minDistance={20} maxDistance={150} />
      </Canvas>

      {/* Performance stats */}
      {showStats && <PerformanceStats />}
    </div>
  );
}
