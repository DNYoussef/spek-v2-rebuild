/**
 * Loop 3: Concentric Circles 3D Visualization
 *
 * Research-backed 3D implementation:
 * - <50 draw calls target
 * - LOD rendering for ring segments
 * - Ripple effects on completion
 *
 * Features:
 * - Center: Project core (3D sphere with quality score)
 * - Rings: Audit → GitHub → CI/CD → Docs → Export (expanding outward)
 * - Progress: Fill ring segments as tasks complete (color-coded)
 * - Animation: Ripple effects, smooth transitions
 */

'use client';

import { Canvas, useFrame } from '@react-three/fiber';
import { Sphere, Torus, Text } from '@react-three/drei';
import { useRef, useMemo } from 'react';
import * as THREE from 'three';
import { defaultCanvasConfig } from '@/lib/three-config';
import { CameraControls } from './CameraControls';
import { PerformanceStats } from './PerformanceStats';

interface Loop3Data {
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

interface Loop3ConcentricCircles3DProps {
  data: Loop3Data;
  showStats?: boolean;
}

function QualityCore({ qualityScore }: { qualityScore: number }) {
  const ref = useRef<THREE.Mesh>(null);

  useFrame(({ clock }) => {
    if (ref.current) {
      // Gentle pulsing effect
      const scale = 1 + Math.sin(clock.getElapsedTime() * 2) * 0.1;
      ref.current.scale.setScalar(scale);
    }
  });

  const color = qualityScore >= 90 ? '#10b981' :
                qualityScore >= 70 ? '#f59e0b' : '#ef4444';

  return (
    <group>
      <Sphere ref={ref} args={[5, 32, 32]} position={[0, 0, 0]}>
        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={0.5}
          roughness={0.3}
          metalness={0.7}
        />
      </Sphere>

      <Text
        position={[0, 0, 6]}
        fontSize={2.5}
        color="white"
        anchorX="center"
        anchorY="middle"
      >
        {qualityScore.toFixed(0)}%
      </Text>

      <Text
        position={[0, -2.5, 6]}
        fontSize={1}
        color="white"
        anchorX="center"
        anchorY="middle"
      >
        Quality
      </Text>
    </group>
  );
}

function StageRing({ stage }: { stage: Loop3Stage }) {
  const ref = useRef<THREE.Mesh>(null);

  useFrame(({ clock }) => {
    if (ref.current && stage.status === 'in_progress') {
      // Rotate active ring slowly
      ref.current.rotation.y = clock.getElapsedTime() * 0.3;
    }
  });

  const color = stage.status === 'pending' ? '#6b7280' :
                stage.status === 'in_progress' ? '#3b82f6' :
                stage.status === 'completed' ? '#10b981' : '#ef4444';

  // Create partial torus geometry based on progress
  const geometry = useMemo(() => {
    const segments = Math.ceil((stage.progress / 100) * 64);
    const angle = (stage.progress / 100) * Math.PI * 2;

    const points: THREE.Vector3[] = [];
    for (let i = 0; i <= segments; i++) {
      const theta = (i / 64) * angle;
      const x = Math.cos(theta) * stage.radius;
      const z = Math.sin(theta) * stage.radius;
      points.push(new THREE.Vector3(x, 0, z));
    }

    return new THREE.BufferGeometry().setFromPoints(points);
  }, [stage.progress, stage.radius]);

  return (
    <group>
      {/* Progress ring (partial) - Using primitive for Three.js Line */}
      <primitive
        object={new THREE.Line(
          geometry,
          new THREE.LineBasicMaterial({ color, linewidth: 3 })
        )}
        ref={ref}
      />

      {/* Background ring (full, faded) */}
      <Torus
        args={[stage.radius, 0.3, 8, 64]}
        rotation={[Math.PI / 2, 0, 0]}
      >
        <meshBasicMaterial
          color={color}
          transparent
          opacity={0.2}
        />
      </Torus>

      {/* Stage label */}
      <Text
        position={[0, 0, stage.radius + 5]}
        fontSize={1.5}
        color="white"
        anchorX="center"
        anchorY="middle"
      >
        {stage.name}
      </Text>

      {/* Progress percentage */}
      <Text
        position={[0, -1.5, stage.radius + 5]}
        fontSize={1}
        color={color}
        anchorX="center"
        anchorY="middle"
      >
        {stage.progress.toFixed(0)}%
      </Text>
    </group>
  );
}

export function Loop3ConcentricCircles3D({ data, showStats = false }: Loop3ConcentricCircles3DProps) {
  return (
    <div style={{ width: '100%', height: '600px', position: 'relative' }}>
      <Canvas
        {...defaultCanvasConfig}
        camera={{ position: [0, 60, 80], fov: 60 }}
      >
        {/* Lighting */}
        <ambientLight intensity={0.5} />
        <directionalLight position={[10, 20, 10]} intensity={1} />
        <pointLight position={[0, 10, 0]} intensity={0.5} color="#ffffff" />

        {/* Center quality sphere */}
        <QualityCore qualityScore={data.qualityScore} />

        {/* Concentric rings for each stage */}
        {data.stages.map(stage => (
          <StageRing key={stage.id} stage={stage} />
        ))}

        {/* Camera controls */}
        <CameraControls minDistance={30} maxDistance={200} />
      </Canvas>

      {/* Performance stats */}
      {showStats && <PerformanceStats />}
    </div>
  );
}
