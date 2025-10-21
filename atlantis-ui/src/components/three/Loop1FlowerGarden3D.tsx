/**
 * Loop 1: Flower Garden 3D Visualization (Bee-Themed)
 *
 * Transformation of OrbitalRing into bee-themed flower garden:
 * - Center: Failure rate → Central hive/garden hub
 * - Ring nodes: Iterations → Flowers (blooming shows progress)
 * - Satellites: Research artifacts → Pollen particles
 * - Animation: Bees pollinating between flowers
 *
 * Performance optimizations:
 * - On-demand rendering (frameloop: "demand")
 * - Max 20 flowers per scene
 * - Instanced rendering for pollen particles
 * - <100 draw calls target
 */

'use client';

import { Canvas, useFrame } from '@react-three/fiber';
import { Text, OrbitControls } from '@react-three/drei';
import { useRef, useMemo, useState } from 'react';
import * as THREE from 'three';
import { defaultCanvasConfig } from '@/lib/three-config';
import { CameraControls } from './CameraControls';
import { PerformanceStats } from './PerformanceStats';
import { LavenderFlower, RoseFlower, DaisyFlower } from './models/Flower3D';
import { WorkerBee } from './models/Bee3D';
import {
  BeeFlightAnimator,
  calculateFlightDuration,
} from '@/lib/three/animations/BeeFlightPath';
import { useAccessibility3D } from '@/hooks/useAccessibility3D';
import { PollenParticles as PollenParticlesInstanced } from './effects/PollenParticles';
import { FPSMonitor } from './utils/FPSMonitor';

interface Loop1FlowerGardenData {
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
  type: 'specification' | 'premortem' | 'research' | 'github' | 'paper' | 'example';
  name: string;
  position: [number, number, number];
}

interface Loop1FlowerGarden3DProps {
  data?: Loop1FlowerGardenData;
  showStats?: boolean;
}

// Default mock data for development
const DEFAULT_DATA: Loop1FlowerGardenData = {
  failureRate: 8.5,
  currentIteration: 6,
  maxIterations: 12,
  iterations: [
    { id: '1', iterationNumber: 1, failureRate: 15.2, timestamp: Date.now() - 86400000 * 11 },
    { id: '2', iterationNumber: 2, failureRate: 12.8, timestamp: Date.now() - 86400000 * 10 },
    { id: '3', iterationNumber: 3, failureRate: 10.5, timestamp: Date.now() - 86400000 * 9 },
    { id: '4', iterationNumber: 4, failureRate: 9.2, timestamp: Date.now() - 86400000 * 8 },
    { id: '5', iterationNumber: 5, failureRate: 8.7, timestamp: Date.now() - 86400000 * 7 },
    { id: '6', iterationNumber: 6, failureRate: 8.5, timestamp: Date.now() - 86400000 * 6 },
  ],
  artifacts: [
    { id: 'a1', name: 'Spec v1', type: 'specification', position: [3, 2, 1] },
    { id: 'a2', name: 'Spec v2', type: 'specification', position: [4, 1, 2] },
    { id: 'a3', name: 'Premortem v1', type: 'premortem', position: [2, 3, -1] },
    { id: 'a4', name: 'Research Doc', type: 'research', position: [-2, 2, 2] },
  ],
};

/**
 * Central hive hub showing overall progress
 */
function CentralHub({ failureRate }: { failureRate: number }) {
  const meshRef = useRef<THREE.Mesh>(null);

  // Pulsing animation based on failure rate
  useFrame(({ clock }) => {
    if (meshRef.current) {
      const pulse = 1 + Math.sin(clock.getElapsedTime() * 2) * 0.05;
      meshRef.current.scale.set(pulse, pulse, pulse);
    }
  });

  const color = failureRate < 5 ? '#27AE60' : failureRate < 15 ? '#F39C12' : '#E74C3C';

  return (
    <group>
      {/* Central sphere (hive core) - EVEN BIGGER */}
      <mesh ref={meshRef}>
        <sphereGeometry args={[8, 32, 32]} />
        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={0.6}
          metalness={0.7}
          roughness={0.3}
        />
      </mesh>

      {/* Failure rate text - EVEN BIGGER */}
      <Text
        position={[0, 0, 9]}
        fontSize={4}
        color="white"
        anchorX="center"
        anchorY="middle"
        outlineWidth={0.2}
        outlineColor="#000000"
      >
        {failureRate.toFixed(1)}%
      </Text>

      {/* Status text */}
      <Text
        position={[0, -1.5, 0]}
        fontSize={0.5}
        color="#FFB300"
        anchorX="center"
        anchorY="middle"
      >
        Failure Rate
      </Text>
    </group>
  );
}

/**
 * Circular flower garden (iterations as flowers)
 */
function FlowerGarden({ iterations }: { iterations: Iteration[] }) {
  const gardenRadius = 30;

  // Calculate flower positions in circular arrangement
  const flowerPositions = useMemo(() => {
    return iterations.slice(0, 20).map((iter, i) => {
      const angle = (i / Math.min(iterations.length, 20)) * Math.PI * 2;
      return {
        iteration: iter,
        position: [
          Math.cos(angle) * gardenRadius,
          0,
          Math.sin(angle) * gardenRadius,
        ] as [number, number, number],
        angle,
      };
    });
  }, [iterations]);

  return (
    <group>
      {/* Garden path (circular) */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.05, 0]}>
        <ringGeometry args={[gardenRadius - 2, gardenRadius + 2, 64]} />
        <meshStandardMaterial
          color="#8B4513"
          roughness={0.9}
          metalness={0.1}
        />
      </mesh>

      {/* Flowers representing iterations */}
      {flowerPositions.map(({ iteration, position }, idx) => {
        const isComplete = idx < iterations.findIndex((i) => i.id === iteration.id);
        const bloomProgress = isComplete ? 1.0 : 0.3;

        // Choose flower type based on failure rate
        const FlowerComponent =
          iteration.failureRate < 5
            ? DaisyFlower // Success (yellow)
            : iteration.failureRate < 15
            ? RoseFlower // Warning (pink)
            : LavenderFlower; // High risk (purple)

        return (
          <FlowerComponent
            key={iteration.id}
            position={position}
            bloomProgress={bloomProgress}
            sway={true}
            scale={8.0}
          />
        );
      })}
    </group>
  );
}

/**
 * Pollinating bee that flies between flowers
 */
function PollinatingBee({ flowers }: { flowers: { position: [number, number, number] }[] }) {
  const beeRef = useRef<THREE.Group>(null);
  const [currentTarget, setCurrentTarget] = useState(0);
  const [animator, setAnimator] = useState<BeeFlightAnimator | null>(null);

  // Initialize animator
  useMemo(() => {
    if (flowers.length < 2) return;

    const start = new THREE.Vector3(...flowers[0].position);
    const end = new THREE.Vector3(...flowers[1].position);
    start.y += 2;
    end.y += 2;

    const newAnimator = new BeeFlightAnimator({
      start,
      end,
      duration: calculateFlightDuration(start, end, 1.5),
      height: 1.5,
      bobFrequency: 3,
      bobAmplitude: 0.2,
    });
    setAnimator(newAnimator);
  }, [flowers]);

  useFrame((state) => {
    if (!beeRef.current || !animator || flowers.length < 2) return;

    const time = state.clock.getElapsedTime();
    const position = animator.getPosition(time);
    const rotation = animator.getRotation();

    beeRef.current.position.copy(position);
    beeRef.current.rotation.copy(rotation);

    // Move to next flower when animation completes
    if (animator.isFinished()) {
      const nextTarget = (currentTarget + 1) % flowers.length;
      const start = new THREE.Vector3(...flowers[currentTarget].position);
      const end = new THREE.Vector3(...flowers[nextTarget].position);
      start.y += 2;
      end.y += 2;

      const newAnimator = new BeeFlightAnimator({
        start,
        end,
        duration: calculateFlightDuration(start, end, 1.5),
        height: 1.5,
        bobFrequency: 3,
        bobAmplitude: 0.2,
      });
      setAnimator(newAnimator);
      setCurrentTarget(nextTarget);
    }
  });

  if (!animator) return null;

  return (
    <group ref={beeRef}>
      <WorkerBee wingSpeed={35} isFlying />
    </group>
  );
}

// Removed unused PollenParticles function - using PollenParticlesInstanced instead (line 388)

/**
 * Main flower garden scene
 */
function FlowerGardenScene({
  data,
  prefersReducedMotion,
}: {
  data: Loop1FlowerGardenData;
  prefersReducedMotion?: boolean;
}) {
  const flowerPositions = useMemo(() => {
    const gardenRadius = 30;
    return data.iterations.slice(0, 20).map((_, i) => {
      const angle = (i / Math.min(data.iterations.length, 20)) * Math.PI * 2;
      return {
        position: [
          Math.cos(angle) * gardenRadius,
          0,
          Math.sin(angle) * gardenRadius,
        ] as [number, number, number],
      };
    });
  }, [data.iterations]);

  return (
    <>
      {/* Lighting */}
      <ambientLight intensity={0.5} />
      <directionalLight position={[10, 20, 10]} intensity={0.8} />
      <pointLight position={[0, 10, 0]} intensity={0.3} color="#FFEF00" />

      {/* Central hub */}
      <CentralHub failureRate={data.failureRate} />

      {/* Flower garden */}
      <FlowerGarden iterations={data.iterations} />

      {/* Pollinating bees (3 bees) */}
      {flowerPositions.length >= 2 && (
        <>
          <PollinatingBee flowers={flowerPositions} />
          <PollinatingBee flowers={flowerPositions.slice(1)} />
          <PollinatingBee flowers={flowerPositions.slice(2)} />
        </>
      )}

      {/* Enhanced pollen particles (Week 19 Day 6: Instanced rendering) */}
      <PollenParticlesInstanced count={300} radius={35} shimmer={!prefersReducedMotion} />

      {/* Ground plane (garden grass) */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.1, 0]}>
        <planeGeometry args={[100, 100]} />
        <meshStandardMaterial
          color="#2ECC71"
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
export default function Loop1FlowerGarden3D({
  data = DEFAULT_DATA,
  showStats = false,
}: Loop1FlowerGarden3DProps) {
  const cameraPosition: [number, number, number] = [30, 20, 30];

  // Accessibility features (Week 19 Day 5)
  const { canvasProps, prefersReducedMotion, handleKeyDown } = useAccessibility3D({
    ariaLabel: 'Loop 1 Flower Garden 3D Visualization',
    ariaDescription: `Interactive 3D visualization showing research and pre-mortem iterations as a bee-themed flower garden. Current failure rate: ${data.failureRate.toFixed(1)}%. Iteration ${data.currentIteration} of ${data.maxIterations}. Use arrow keys to rotate camera, plus and minus to zoom.`,
    currentState: `Iteration ${data.currentIteration} of ${data.maxIterations}, failure rate ${data.failureRate.toFixed(1)}%`,
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
        <FlowerGardenScene data={data} prefersReducedMotion={prefersReducedMotion} />
        {/* Interactive camera controls */}
        <OrbitControls
          enableDamping={!prefersReducedMotion}
          dampingFactor={0.05}
          minDistance={15}
          maxDistance={100}
          enableRotate={!prefersReducedMotion}
          autoRotate={false}
        />
        {showStats && <FPSMonitor targetFPS={60} showOverlay={true} />}
      </Canvas>

      {showStats && <PerformanceStats />}

      {/* Hidden description for screen readers */}
      {canvasProps['aria-describedby'] && (
        <div id={canvasProps['aria-describedby']} className="sr-only">
          <p>
            Interactive 3D visualization showing research and pre-mortem iterations as a bee-themed flower garden.
            Current failure rate: {data.failureRate.toFixed(1)}%.
            Iteration {data.currentIteration} of {data.maxIterations}.
            Use arrow keys to rotate camera, plus and minus to zoom, R to reset view.
          </p>
        </div>
      )}
    </div>
  );
}
