/**
 * Adaptive Visualizer Component
 *
 * Automatically selects 2D or 3D visualization based on:
 * - GPU memory (<400MB triggers 2D fallback)
 * - File count (>5000 files triggers 2D fallback)
 * - User preference (manual toggle)
 *
 * Research-backed graceful degradation strategy
 */

'use client';

import { useState, useEffect, ReactNode } from 'react';
import { shouldUse3D, detectGPUCapabilities } from '@/lib/three-config';

interface AdaptiveVisualizerProps {
  fileCount: number;
  component2D: ReactNode;
  component3D: ReactNode;
  defaultMode?: '2d' | '3d' | 'auto';
}

export function AdaptiveVisualizer({
  fileCount,
  component2D,
  component3D,
  defaultMode = 'auto'
}: AdaptiveVisualizerProps) {
  const [mode, setMode] = useState<'2d' | '3d'>('2d');
  const [userOverride, setUserOverride] = useState<'2d' | '3d' | null>(null);
  const [gpuInfo, setGPUInfo] = useState<string>('Detecting...');

  useEffect(() => {
    // Detect GPU capabilities
    const capabilities = detectGPUCapabilities();

    if (!capabilities) {
      setGPUInfo('WebGL not supported');
      setMode('2d');
      return;
    }

    setGPUInfo(`${capabilities.renderer} (${capabilities.memory.toFixed(0)}MB)`);

    // Determine mode
    if (defaultMode === 'auto') {
      const use3D = shouldUse3D(fileCount);
      setMode(use3D ? '3d' : '2d');
    } else {
      setMode(defaultMode);
    }
  }, [fileCount, defaultMode]);

  const currentMode = userOverride || mode;

  const toggleMode = () => {
    setUserOverride(currentMode === '2d' ? '3d' : '2d');
  };

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%' }}>
      {/* Mode indicator and toggle */}
      <div style={{
        position: 'absolute',
        top: 10,
        right: 10,
        zIndex: 1000,
        background: 'rgba(0, 0, 0, 0.7)',
        color: 'white',
        padding: '8px 12px',
        borderRadius: '4px',
        display: 'flex',
        flexDirection: 'column',
        gap: '8px',
        fontSize: '12px'
      }}>
        <div>
          <strong>Mode:</strong> {currentMode.toUpperCase()}
          {userOverride && ' (Manual)'}
        </div>
        <div style={{ fontSize: '10px', color: '#aaa' }}>
          GPU: {gpuInfo}
        </div>
        <button
          onClick={toggleMode}
          style={{
            padding: '4px 8px',
            background: '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '11px'
          }}
        >
          Switch to {currentMode === '2d' ? '3D' : '2D'}
        </button>
      </div>

      {/* Render appropriate component */}
      {currentMode === '2d' ? component2D : component3D}
    </div>
  );
}
