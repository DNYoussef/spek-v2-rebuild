/**
 * Enhanced Bee Wing Shimmer Animation
 * Week 19 Day 6
 *
 * Iridescent shimmer effect for bee wings using custom shaders.
 * Creates rainbow/golden shimmer as wings flap.
 *
 * Performance:
 * - GPU-based shader animation
 * - No CPU overhead
 * - Works with existing Bee3D models
 */

'use client';

import { useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

/**
 * Custom shader material for bee wing shimmer
 */
export function createWingShimmerMaterial(baseColor: string = '#E8F5E9') {
  const material = new THREE.ShaderMaterial({
    uniforms: {
      time: { value: 0 },
      baseColor: { value: new THREE.Color(baseColor) },
      shimmerColor: { value: new THREE.Color('#FFB300') },
      shimmerIntensity: { value: 0.6 },
    },
    vertexShader: `
      varying vec2 vUv;
      varying vec3 vNormal;
      varying vec3 vViewPosition;

      void main() {
        vUv = uv;
        vNormal = normalize(normalMatrix * normal);

        vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
        vViewPosition = -mvPosition.xyz;

        gl_Position = projectionMatrix * mvPosition;
      }
    `,
    fragmentShader: `
      uniform float time;
      uniform vec3 baseColor;
      uniform vec3 shimmerColor;
      uniform float shimmerIntensity;

      varying vec2 vUv;
      varying vec3 vNormal;
      varying vec3 vViewPosition;

      void main() {
        // Fresnel effect (edges glow more)
        vec3 viewDir = normalize(vViewPosition);
        float fresnel = pow(1.0 - abs(dot(vNormal, viewDir)), 2.0);

        // Animated shimmer wave
        float wave = sin(vUv.x * 10.0 + time * 3.0) * 0.5 + 0.5;
        float shimmer = wave * fresnel * shimmerIntensity;

        // Iridescent color shift
        vec3 iridescent = mix(
          shimmerColor,
          vec3(1.0, 0.9, 0.3), // Golden-white
          sin(time * 2.0 + vUv.y * 5.0) * 0.5 + 0.5
        );

        // Combine base color with shimmer
        vec3 finalColor = mix(baseColor, iridescent, shimmer);

        // Add transparency on edges
        float alpha = 0.7 + fresnel * 0.3;

        gl_FragColor = vec4(finalColor, alpha);
      }
    `,
    transparent: true,
    side: THREE.DoubleSide,
  });

  return material;
}

/**
 * Hook to animate wing shimmer material
 */
export function useWingShimmerAnimation(
  materialRef: React.RefObject<THREE.ShaderMaterial>,
  wingSpeed: number = 30
) {
  useFrame(({ clock }) => {
    if (!materialRef.current) return;

    // Update time uniform for shader animation
    materialRef.current.uniforms.time.value = clock.getElapsedTime() * (wingSpeed / 30);
  });
}

/**
 * Example usage component (for reference)
 */
export function BeeWithShimmer() {
  const wingMaterial = useMemo(() => createWingShimmerMaterial('#E8F5E9'), []);
  const materialRef = { current: wingMaterial };

  useWingShimmerAnimation(materialRef, 35);

  return (
    <group>
      {/* Left wing */}
      <mesh position={[-0.3, 0, 0]} rotation={[0, 0, Math.PI / 6]}>
        <planeGeometry args={[0.5, 0.3]} />
        <primitive object={wingMaterial} attach="material" />
      </mesh>

      {/* Right wing */}
      <mesh position={[0.3, 0, 0]} rotation={[0, 0, -Math.PI / 6]}>
        <planeGeometry args={[0.5, 0.3]} />
        <primitive object={wingMaterial} attach="material" />
      </mesh>
    </group>
  );
}
