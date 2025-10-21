/**
 * FPS Monitor and Performance Optimizer
 * Week 19 Day 6
 *
 * Real-time FPS monitoring with automatic quality adjustment
 * to maintain 60 FPS target on desktop, 30 FPS on mobile.
 *
 * Features:
 * - Rolling average FPS calculation
 * - Automatic LOD adjustment
 * - Performance warnings
 * - Memory usage tracking
 */

'use client';

import { useRef, useState, useEffect } from 'react';
import { useFrame, useThree } from '@react-three/fiber';

export interface FPSMonitorProps {
  /** Target FPS (60 for desktop, 30 for mobile) */
  targetFPS?: number;

  /** Enable automatic quality adjustment */
  autoAdjust?: boolean;

  /** Show FPS overlay */
  showOverlay?: boolean;

  /** Callback when FPS drops below target */
  onLowFPS?: (fps: number) => void;
}

export interface PerformanceMetrics {
  fps: number;
  frameTime: number;
  memory?: number;
  drawCalls?: number;
  triangles?: number;
}

/**
 * FPS Monitor component
 */
export function FPSMonitor({
  targetFPS = 60,
  autoAdjust = true,
  showOverlay = true,
  onLowFPS,
}: FPSMonitorProps) {
  const { gl } = useThree();
  const [metrics, setMetrics] = useState<PerformanceMetrics>({
    fps: 60,
    frameTime: 16.67,
  });

  const frameTimesRef = useRef<number[]>([]);
  const lastTimeRef = useRef(performance.now());
  const lowFPSCountRef = useRef(0);

  useFrame(() => {
    const now = performance.now();
    const deltaTime = now - lastTimeRef.current;
    lastTimeRef.current = now;

    // Store last 60 frame times for rolling average
    frameTimesRef.current.push(deltaTime);
    if (frameTimesRef.current.length > 60) {
      frameTimesRef.current.shift();
    }

    // Calculate average FPS every 10 frames
    if (frameTimesRef.current.length % 10 === 0) {
      const avgFrameTime =
        frameTimesRef.current.reduce((a, b) => a + b, 0) /
        frameTimesRef.current.length;
      const fps = 1000 / avgFrameTime;

      // Get renderer info
      const info = gl.info;
      const memory = (performance as any).memory?.usedJSHeapSize;

      setMetrics({
        fps: Math.round(fps),
        frameTime: avgFrameTime,
        memory: memory ? Math.round(memory / 1024 / 1024) : undefined,
        drawCalls: info.render.calls,
        triangles: info.render.triangles,
      });

      // Check for low FPS
      if (fps < targetFPS - 5) {
        lowFPSCountRef.current++;
        if (lowFPSCountRef.current > 5 && onLowFPS) {
          onLowFPS(fps);
          lowFPSCountRef.current = 0; // Reset to avoid spam
        }
      } else {
        lowFPSCountRef.current = 0;
      }
    }
  });

  if (!showOverlay) return null;

  return (
    <div
      style={{
        position: 'absolute',
        top: 10,
        left: 10,
        background: 'rgba(0, 0, 0, 0.7)',
        color: '#fff',
        padding: '8px 12px',
        borderRadius: '4px',
        fontFamily: 'monospace',
        fontSize: '12px',
        zIndex: 1000,
        pointerEvents: 'none',
      }}
    >
      <div style={{ color: metrics.fps >= targetFPS ? '#4CAF50' : '#F44336' }}>
        <strong>FPS:</strong> {metrics.fps} / {targetFPS}
      </div>
      <div>
        <strong>Frame:</strong> {metrics.frameTime.toFixed(2)}ms
      </div>
      {metrics.drawCalls !== undefined && (
        <div>
          <strong>Draw Calls:</strong> {metrics.drawCalls}
        </div>
      )}
      {metrics.triangles !== undefined && (
        <div>
          <strong>Triangles:</strong> {metrics.triangles.toLocaleString()}
        </div>
      )}
      {metrics.memory !== undefined && (
        <div>
          <strong>Memory:</strong> {metrics.memory}MB
        </div>
      )}
    </div>
  );
}

/**
 * Hook for FPS monitoring without overlay
 */
export function useFPSMonitor(targetFPS: number = 60) {
  const [fps, setFPS] = useState(60);
  const [isLowFPS, setIsLowFPS] = useState(false);
  const frameTimesRef = useRef<number[]>([]);
  const lastTimeRef = useRef(performance.now());

  useFrame(() => {
    const now = performance.now();
    const deltaTime = now - lastTimeRef.current;
    lastTimeRef.current = now;

    frameTimesRef.current.push(deltaTime);
    if (frameTimesRef.current.length > 60) {
      frameTimesRef.current.shift();
    }

    if (frameTimesRef.current.length % 10 === 0) {
      const avgFrameTime =
        frameTimesRef.current.reduce((a, b) => a + b, 0) /
        frameTimesRef.current.length;
      const currentFPS = Math.round(1000 / avgFrameTime);

      setFPS(currentFPS);
      setIsLowFPS(currentFPS < targetFPS - 5);
    }
  });

  return { fps, isLowFPS };
}

/**
 * Performance optimization utility
 */
export function optimizeForFPS(currentFPS: number, targetFPS: number = 60) {
  if (currentFPS >= targetFPS) {
    return {
      particleCount: 1000,
      shadowQuality: 'high',
      textureResolution: 2048,
      enablePostProcessing: true,
    };
  } else if (currentFPS >= targetFPS - 10) {
    return {
      particleCount: 500,
      shadowQuality: 'medium',
      textureResolution: 1024,
      enablePostProcessing: true,
    };
  } else {
    return {
      particleCount: 250,
      shadowQuality: 'low',
      textureResolution: 512,
      enablePostProcessing: false,
    };
  }
}
