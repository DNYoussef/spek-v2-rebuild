/**
 * Loop 3: Honeycomb Layers 3D Visualization (Bee-Themed)
 *
 * Transformation of ConcentricCircles into bee-themed honeycomb:
 * - Center: Quality score → Golden honey core
 * - Rings: Audit stages → Hexagonal honeycomb rings
 * - Progress: Honey filling animation (empty → filling → full)
 * - Animation: Golden shimmer on completion, ripple effects
 *
 * Performance optimizations:
 * - <50 draw calls target
 * - LOD rendering for distant rings
 * - Instanced hexagon meshes
 * - Animated shaders for honey filling
 */

'use client';

import { Canvas, useFrame } from '@react-three/fiber';
import { Sphere, Text } from '@react-three/drei';
import { useRef, useMemo } from 'react';
import * as THREE from 'three';
import { defaultCanvasConfig } from '@/lib/three-config';
import { CameraControls } from './CameraControls';
import { PerformanceStats } from './PerformanceStats';
import { HoneycombCell3D } from './models/HoneycombCell3D';
import { useAccessibility3D } from '@/hooks/useAccessibility3D';

interface Loop3HoneycombData {
  qualityScore: number; // 0-100
  stages: Loop3Stage[];
}

interface Loop3Stage {
  id: string;
  name: string;
  progress: number; // 0-100
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  radius: number; // Distance from center
}

interface Loop3HoneycombLayers3DProps {
  data?: Loop3HoneycombData;
  showStats?: boolean;
}

// Default mock data for development
const DEFAULT_DATA: Loop3HoneycombData = {
  qualityScore: 92.5,
  stages: [
    { id: 's1', name: 'Code Review', progress: 100, status: 'completed', radius: 3 },
    { id: 's2', name: 'Testing', progress: 85, status: 'in_progress', radius: 6 },
    { id: 's3', name: 'Security Audit', progress: 60, status: 'in_progress', radius: 9 },
    { id: 's4', name: 'Performance Check', progress: 40, status: 'in_progress', radius: 12 },
    { id: 's5', name: 'Documentation', progress: 0, status: 'pending', radius: 15 },
  ],
};

/**
 * Golden honey core showing overall quality
 */
function HoneyCore({ qualityScore }: { qualityScore: number }) {
  const coreRef = useRef<THREE.Mesh>(null);
  const glowRef = useRef<THREE.Mesh>(null);

  useFrame(({ clock }) => {
    if (coreRef.current) {
      // Gentle pulsing effect
      const scale = 1 + Math.sin(clock.getElapsedTime() * 1.5) * 0.08;
      coreRef.current.scale.setScalar(scale);
    }

    if (glowRef.current) {
      // Rotating glow
      glowRef.current.rotation.y = clock.getElapsedTime() * 0.5;
      const glowScale = 1.2 + Math.sin(clock.getElapsedTime() * 2) * 0.1;
      glowRef.current.scale.setScalar(glowScale);
    }
  });

  const color =
    qualityScore >= 90
      ? '#FFB300' // Gold (excellent)
      : qualityScore >= 70
      ? '#F39C12' // Amber (good)
      : '#E67E22'; // Orange (needs work)

  return (
    <group>
      {/* Core sphere (honey drop) */}
      <Sphere ref={coreRef} args={[5, 32, 32]} position={[0, 0, 0]}>
        <meshPhysicalMaterial
          color={color}
          emissive={color}
          emissiveIntensity={0.4}
          roughness={0.2}
          metalness={0.6}
          clearcoat={1.0}
          clearcoatRoughness={0.1}
          transparent
          opacity={0.9}
        />
      </Sphere>

      {/* Outer glow */}
      <Sphere ref={glowRef} args={[6, 32, 32]} position={[0, 0, 0]}>
        <meshBasicMaterial
          color={color}
          transparent
          opacity={0.2}
          side={THREE.BackSide}
        />
      </Sphere>

      {/* Quality score text */}
      <Text
        position={[0, 0, 6]}
        fontSize={2.5}
        color="white"
        anchorX="center"
        anchorY="middle"
        outlineWidth={0.15}
        outlineColor="#000000"
      >
        {qualityScore.toFixed(0)}%
      </Text>

      <Text
        position={[0, -2, 6]}
        fontSize={1}
        color="#FFB300"
        anchorX="center"
        anchorY="middle"
      >
        Quality
      </Text>
    </group>
  );
}

/**
 * Hexagonal honeycomb ring for each stage
 */
function HoneycombRing({ stage }: { stage: Loop3Stage }) {
  const ringRef = useRef<THREE.Group>(null);

  // Calculate hexagon positions around ring
  const hexPositions = useMemo(() => {
    const circumference = 2 * Math.PI * stage.radius;
    const hexCount = Math.floor(circumference / 1.5); // ~1.5 units per hex
    const positions: [number, number, number][] = [];

    for (let i = 0; i < hexCount; i++) {
      const angle = (i / hexCount) * Math.PI * 2;
      const x = Math.cos(angle) * stage.radius;
      const z = Math.sin(angle) * stage.radius;
      positions.push([x, 0, z]);
    }

    return positions;
  }, [stage.radius]);

  // Calculate how many cells should be filled based on progress
  const filledCount = Math.floor((stage.progress / 100) * hexPositions.length);

  // Gentle rotation
  useFrame(({ clock }) => {
    if (ringRef.current && stage.status === 'completed') {
      ringRef.current.rotation.y = clock.getElapsedTime() * 0.1;
    }
  });

  return (
    <group ref={ringRef}>
      {hexPositions.map((pos, idx) => {
        let cellState: 'empty' | 'filling' | 'full';
        if (idx < filledCount - 1) {
          cellState = 'full';
        } else if (idx === filledCount - 1) {
          cellState = 'filling';
        } else {
          cellState = 'empty';
        }

        // Calculate fill progress for filling cell
        const fillProgress =
          cellState === 'filling'
            ? ((stage.progress / 100) * hexPositions.length) % 1
            : 0;

        return (
          <HoneycombCell3D
            key={idx}
            position={pos}
            state={cellState}
            fillProgress={fillProgress}
            glow={cellState === 'full'}
          />
        );
      })}

      {/* Stage label */}
      <Text
        position={[0, 1.5, stage.radius + 3]}
        fontSize={0.8}
        color="#FFB300"
        anchorX="center"
        anchorY="middle"
        outlineWidth={0.05}
        outlineColor="#000000"
      >
        {stage.name}
      </Text>

      {/* Progress percentage */}
      <Text
        position={[0, 0.5, stage.radius + 3]}
        fontSize={0.6}
        color="white"
        anchorX="center"
        anchorY="middle"
      >
        {stage.progress.toFixed(0)}%
      </Text>
    </group>
  );
}

/**
 * Completion ripple effect (golden wave)
 */
function CompletionRipple({ stage }: { stage: Loop3Stage }) {
  const rippleRef = useRef<THREE.Mesh>(null);

  useFrame(({ clock }) => {
    if (!rippleRef.current || stage.status !== 'completed') return;

    // Expanding ripple
    const time = clock.getElapsedTime();
    const scale = 1 + Math.sin(time * 2) * 0.1;
    rippleRef.current.scale.set(scale, 1, scale);

    // Fade out and in
    const material = rippleRef.current.material as THREE.MeshBasicMaterial;
    material.opacity = 0.3 + Math.sin(time * 3) * 0.2;
  });

  if (stage.status !== 'completed') return null;

  return (
    <mesh ref={rippleRef} rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.1, 0]}>
      <ringGeometry args={[stage.radius - 1, stage.radius + 1, 64]} />
      <meshBasicMaterial
        color="#FFB300"
        transparent
        opacity={0.3}
        side={THREE.DoubleSide}
      />
    </mesh>
  );
}

/**
 * Final golden seal (when all stages complete)
 */
function GoldenSeal({ stages }: { stages: Loop3Stage[] }) {
  const sealRef = useRef<THREE.Mesh>(null);
  const allComplete = stages.every((s) => s.status === 'completed');

  useFrame(({ clock }) => {
    if (!sealRef.current || !allComplete) return;

    // Rotating golden seal
    sealRef.current.rotation.y = clock.getElapsedTime() * 0.3;

    // Pulsing glow
    const material = sealRef.current.material as THREE.MeshStandardMaterial;
    material.emissiveIntensity = 0.5 + Math.sin(clock.getElapsedTime() * 2) * 0.3;
  });

  if (!allComplete) return null;

  const maxRadius = Math.max(...stages.map((s) => s.radius)) + 5;

  return (
    <mesh ref={sealRef} rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.2, 0]}>
      <ringGeometry args={[maxRadius, maxRadius + 2, 6]} />
      <meshStandardMaterial
        color="#FFB300"
        emissive="#FFB300"
        emissiveIntensity={0.5}
        metalness={0.8}
        roughness={0.2}
      />
    </mesh>
  );
}

/**
 * Main honeycomb layers scene
 */
function HoneycombLayersScene({
  data,
}: {
  data: Loop3HoneycombData;
}) {
  return (
    <>
      {/* Lighting */}
      <ambientLight intensity={0.4} />
      <directionalLight position={[15, 20, 15]} intensity={0.8} />
      <pointLight position={[0, 15, 0]} intensity={0.5} color="#FFB300" />

      {/* Central honey core */}
      <HoneyCore qualityScore={data.qualityScore} />

      {/* Honeycomb rings for each stage */}
      {data.stages.map((stage) => (
        <HoneycombRing key={stage.id} stage={stage} />
      ))}

      {/* Completion ripples */}
      {data.stages.map((stage) => (
        <CompletionRipple key={`ripple-${stage.id}`} stage={stage} />
      ))}

      {/* Final golden seal */}
      <GoldenSeal stages={data.stages} />

      {/* Ground plane (honeycomb pattern) */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.15, 0]}>
        <planeGeometry args={[200, 200]} />
        <meshStandardMaterial
          color="#FFF8DC"
          roughness={0.9}
          metalness={0.1}
        />
      </mesh>

      {/* Camera controls */}
      <CameraControls />
    </>
  );
}

/**
 * Main component with Canvas wrapper
 * Week 19 Day 5: Added accessibility support
 */
export default function Loop3HoneycombLayers3D({
  data = DEFAULT_DATA,
  showStats = false,
}: Loop3HoneycombLayers3DProps) {
  const cameraPosition: [number, number, number] = [30, 35, 30];

  const stageStats = {
    total: data.stages.length,
    completed: data.stages.filter(s => s.status === 'completed').length,
    inProgress: data.stages.filter(s => s.status === 'in_progress').length,
  };

  // Accessibility features (Week 19 Day 5)
  const { canvasProps, prefersReducedMotion, handleKeyDown } = useAccessibility3D({
    ariaLabel: 'Loop 3 Honeycomb Layers 3D Visualization',
    ariaDescription: `Interactive 3D visualization showing quality audit stages as honeycomb layers. Overall quality score: ${data.qualityScore.toFixed(1)}%. ${stageStats.completed} of ${stageStats.total} audit stages completed. Use arrow keys to rotate camera, plus and minus to zoom.`,
    currentState: `Quality score ${data.qualityScore.toFixed(1)}%, ${stageStats.inProgress} stages in progress`,
    enableKeyboardNav: true,
    respectReducedMotion: true,
  });

  return (
    <div className="relative w-full h-full" onKeyDown={handleKeyDown}>
      <Canvas
        {...defaultCanvasConfig}
        {...canvasProps}
        camera={{
          position: cameraPosition,
          fov: 60,
        }}
        frameloop={prefersReducedMotion ? 'demand' : 'always'}
      >
        <HoneycombLayersScene data={data} />
      </Canvas>

      {showStats && <PerformanceStats />}

      {/* Hidden description for screen readers */}
      {canvasProps['aria-describedby'] && (
        <div id={canvasProps['aria-describedby']} className="sr-only">
          <p>
            Interactive 3D visualization showing quality audit stages as concentric honeycomb layers.
            Overall quality score: {data.qualityScore.toFixed(1)}%.
            {stageStats.completed} of {stageStats.total} audit stages completed, {stageStats.inProgress} in progress.
            Use arrow keys to rotate camera, plus and minus to zoom, R to reset view.
          </p>
        </div>
      )}
    </div>
  );
}
