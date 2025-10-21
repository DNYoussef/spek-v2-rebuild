'use client';

import { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

/**
 * Bee3D - 3D bee model with animated wings
 *
 * Represents an AI agent as a bee in the hive visualization.
 * Includes body, head, wings, and legs with realistic animation.
 *
 * Props:
 * - position: [x, y, z] position in 3D space
 * - scale: Size multiplier (1.0 = normal, 1.5 = queen, 1.2 = princess)
 * - color: Bee body color (default: bee gold)
 * - wingSpeed: Wing flap speed in Hz (default: 30)
 * - isFlying: Whether bee is in flight (affects animation)
 */

interface Bee3DProps {
  position?: [number, number, number];
  scale?: number;
  color?: string;
  accentColor?: string;
  wingSpeed?: number;
  isFlying?: boolean;
  onClick?: () => void;
}

export function Bee3D({
  position = [0, 0, 0],
  scale = 1.0,
  color = '#FFB300',
  accentColor = '#000000',
  wingSpeed = 30,
  isFlying = true,
  onClick,
}: Bee3DProps) {
  const groupRef = useRef<THREE.Group>(null);
  const leftWingRef = useRef<THREE.Mesh>(null);
  const rightWingRef = useRef<THREE.Mesh>(null);

  // Wing flap animation
  useFrame((state) => {
    if (!leftWingRef.current || !rightWingRef.current) return;

    const time = state.clock.getElapsedTime();
    const flapFrequency = wingSpeed / 60; // Convert Hz to radians/frame
    const flapAngle = Math.sin(time * flapFrequency * Math.PI * 2) * 0.5;

    // Animate wings
    leftWingRef.current.rotation.z = flapAngle;
    rightWingRef.current.rotation.z = -flapAngle;

    // Bobbing motion if flying
    if (isFlying && groupRef.current) {
      groupRef.current.position.y =
        position[1] + Math.sin(time * 2) * 0.1;
    }
  });

  // Create bee materials
  const bodyMaterial = useMemo(
    () =>
      new THREE.MeshStandardMaterial({
        color: new THREE.Color(color),
        metalness: 0.3,
        roughness: 0.7,
      }),
    [color]
  );

  const stripeMaterial = useMemo(
    () =>
      new THREE.MeshStandardMaterial({
        color: new THREE.Color(accentColor),
        metalness: 0.2,
        roughness: 0.8,
      }),
    [accentColor]
  );

  const wingMaterial = useMemo(
    () =>
      new THREE.MeshPhysicalMaterial({
        color: 0xffffff,
        transparent: true,
        opacity: 0.3,
        metalness: 0.1,
        roughness: 0.1,
        clearcoat: 1.0,
        clearcoatRoughness: 0.1,
      }),
    []
  );

  return (
    <group
      ref={groupRef}
      position={position}
      scale={scale}
      onClick={onClick}
    >
      {/* Body (ellipsoid with stripes) */}
      <mesh material={bodyMaterial}>
        <sphereGeometry args={[0.3, 16, 16]} />
        <meshStandardMaterial
          color={color}
          metalness={0.3}
          roughness={0.7}
        />
      </mesh>

      {/* Black stripes */}
      <mesh position={[0, 0.1, 0]} scale={[1, 0.3, 1]}>
        <sphereGeometry args={[0.31, 16, 8]} />
        <meshStandardMaterial {...stripeMaterial} />
      </mesh>
      <mesh position={[0, -0.1, 0]} scale={[1, 0.3, 1]}>
        <sphereGeometry args={[0.31, 16, 8]} />
        <meshStandardMaterial {...stripeMaterial} />
      </mesh>

      {/* Head */}
      <mesh position={[0, 0, 0.35]}>
        <sphereGeometry args={[0.2, 16, 16]} />
        <meshStandardMaterial
          color={accentColor}
          metalness={0.2}
          roughness={0.8}
        />
      </mesh>

      {/* Antennae */}
      <mesh position={[-0.08, 0.15, 0.45]} rotation={[0.3, -0.3, 0]}>
        <cylinderGeometry args={[0.01, 0.01, 0.15, 8]} />
        <meshStandardMaterial color={accentColor} />
      </mesh>
      <mesh position={[0.08, 0.15, 0.45]} rotation={[0.3, 0.3, 0]}>
        <cylinderGeometry args={[0.01, 0.01, 0.15, 8]} />
        <meshStandardMaterial color={accentColor} />
      </mesh>

      {/* Left Wing */}
      <mesh
        ref={leftWingRef}
        position={[-0.2, 0, 0]}
        rotation={[0, 0, 0]}
      >
        <planeGeometry args={[0.5, 0.3]} />
        <meshPhysicalMaterial {...wingMaterial} />
      </mesh>

      {/* Right Wing */}
      <mesh
        ref={rightWingRef}
        position={[0.2, 0, 0]}
        rotation={[0, 0, 0]}
      >
        <planeGeometry args={[0.5, 0.3]} />
        <meshPhysicalMaterial {...wingMaterial} />
      </mesh>

      {/* Legs (6 legs, simplified) */}
      {[-0.15, 0, 0.15].map((xPos, i) => (
        <group key={`leg-${i}`}>
          <mesh
            position={[xPos - 0.05, -0.25, 0.05]}
            rotation={[0.5, 0, 0]}
          >
            <cylinderGeometry args={[0.015, 0.015, 0.2, 6]} />
            <meshStandardMaterial color={accentColor} />
          </mesh>
          <mesh
            position={[xPos + 0.05, -0.25, 0.05]}
            rotation={[0.5, 0, 0]}
          >
            <cylinderGeometry args={[0.015, 0.015, 0.2, 6]} />
            <meshStandardMaterial color={accentColor} />
          </mesh>
        </group>
      ))}
    </group>
  );
}

/**
 * Bee variants for different agent types
 */

export function QueenBee(props: Omit<Bee3DProps, 'scale' | 'color'>) {
  return (
    <Bee3D
      {...props}
      scale={1.5}
      color="#9B59B6"
      accentColor="#2C3E50"
    />
  );
}

export function PrincessBee(
  props: Omit<Bee3DProps, 'scale' | 'color'>
) {
  return (
    <Bee3D
      {...props}
      scale={1.2}
      color="#FF69B4"
      accentColor="#34495E"
    />
  );
}

export function WorkerBee(props: Omit<Bee3DProps, 'scale' | 'color'>) {
  return (
    <Bee3D {...props} scale={1.0} color="#FFB300" accentColor="#000000" />
  );
}
