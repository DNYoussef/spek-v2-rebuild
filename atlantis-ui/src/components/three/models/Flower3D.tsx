'use client';

import { useRef, useMemo, useState, useEffect } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

/**
 * Flower3D - 3D flower model with blooming animation
 *
 * Represents project phases as flowers that bloom when complete.
 * Three variants: Lavender (research), Rose (execution), Daisy (quality).
 *
 * Props:
 * - position: [x, y, z] position in 3D space
 * - type: 'lavender' | 'rose' | 'daisy'
 * - bloomProgress: 0-1 (0 = bud, 1 = full bloom)
 * - sway: Enable gentle swaying animation
 */

interface Flower3DProps {
  position?: [number, number, number];
  type?: 'lavender' | 'rose' | 'daisy';
  bloomProgress?: number;
  sway?: boolean;
  scale?: number;
  onClick?: () => void;
}

const FLOWER_COLORS = {
  lavender: {
    petal: '#E6E6FA',
    center: '#9B59B6',
    stem: '#2ECC71',
  },
  rose: {
    petal: '#FF69B4',
    center: '#FFE4B5',
    stem: '#27AE60',
  },
  daisy: {
    petal: '#FFFAF0',
    center: '#FFEF00',
    stem: '#229954',
  },
};

export function Flower3D({
  position = [0, 0, 0],
  type = 'daisy',
  bloomProgress = 1.0,
  sway = true,
  scale = 1.0,
  onClick,
}: Flower3DProps) {
  const groupRef = useRef<THREE.Group>(null);
  const petalsRef = useRef<THREE.Group>(null);
  const [animatedBloom, setAnimatedBloom] = useState(bloomProgress);

  const colors = FLOWER_COLORS[type];
  const petalCount = type === 'rose' ? 8 : type === 'lavender' ? 6 : 8;

  // Animate bloom progress
  useEffect(() => {
    const start = animatedBloom;
    const end = bloomProgress;
    const duration = 1500; // 1.5 seconds
    const startTime = Date.now();

    const animate = () => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3); // Ease-out cubic
      setAnimatedBloom(start + (end - start) * eased);

      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };

    if (Math.abs(end - start) > 0.01) {
      animate();
    }
  }, [bloomProgress]);

  // Swaying animation
  useFrame((state) => {
    if (!groupRef.current || !sway) return;

    const time = state.clock.getElapsedTime();
    groupRef.current.rotation.z = Math.sin(time * 0.5) * 0.05;
    groupRef.current.rotation.x = Math.cos(time * 0.3) * 0.03;
  });

  // Materials
  const petalMaterial = useMemo(
    () =>
      new THREE.MeshStandardMaterial({
        color: new THREE.Color(colors.petal),
        metalness: 0.1,
        roughness: 0.6,
        side: THREE.DoubleSide,
      }),
    [colors.petal]
  );

  const centerMaterial = useMemo(
    () =>
      new THREE.MeshStandardMaterial({
        color: new THREE.Color(colors.center),
        metalness: 0.2,
        roughness: 0.8,
      }),
    [colors.center]
  );

  const stemMaterial = useMemo(
    () =>
      new THREE.MeshStandardMaterial({
        color: new THREE.Color(colors.stem),
        metalness: 0.1,
        roughness: 0.9,
      }),
    [colors.stem]
  );

  return (
    <group
      ref={groupRef}
      position={position}
      scale={scale}
      onClick={onClick}
    >
      {/* Stem */}
      <mesh position={[0, -0.5, 0]} rotation={[0, 0, 0]}>
        <cylinderGeometry args={[0.02, 0.03, 1, 8]} />
        <meshStandardMaterial {...stemMaterial} />
      </mesh>

      {/* Leaves */}
      <mesh position={[-0.1, -0.3, 0]} rotation={[0, 0, -0.5]}>
        <planeGeometry args={[0.15, 0.25]} />
        <meshStandardMaterial {...stemMaterial} side={THREE.DoubleSide} />
      </mesh>
      <mesh position={[0.1, -0.5, 0]} rotation={[0, 0, 0.5]}>
        <planeGeometry args={[0.15, 0.25]} />
        <meshStandardMaterial {...stemMaterial} side={THREE.DoubleSide} />
      </mesh>

      {/* Petals (rotate around center) */}
      <group ref={petalsRef} scale={animatedBloom}>
        {Array.from({ length: petalCount }).map((_, i) => {
          const angle = (Math.PI * 2 * i) / petalCount;
          const x = Math.cos(angle) * 0.2;
          const z = Math.sin(angle) * 0.2;
          const rotation = angle + Math.PI / 2;

          return (
            <mesh
              key={i}
              position={[x, 0, z]}
              rotation={[0.3, rotation, 0]}
            >
              <planeGeometry args={[0.25, 0.35]} />
              <meshStandardMaterial {...petalMaterial} />
            </mesh>
          );
        })}
      </group>

      {/* Center (pollen) */}
      <mesh position={[0, 0, 0]} scale={animatedBloom}>
        <sphereGeometry args={[0.12, 16, 16]} />
        <meshStandardMaterial {...centerMaterial} />
      </mesh>
    </group>
  );
}

/**
 * Flower variants for different loop phases
 */

export function LavenderFlower(
  props: Omit<Flower3DProps, 'type'>
) {
  return <Flower3D {...props} type="lavender" />;
}

export function RoseFlower(props: Omit<Flower3DProps, 'type'>) {
  return <Flower3D {...props} type="rose" />;
}

export function DaisyFlower(props: Omit<Flower3DProps, 'type'>) {
  return <Flower3D {...props} type="daisy" />;
}
