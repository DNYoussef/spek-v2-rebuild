/**
 * Loop 3 Visualizer - Quality Finalization Visualization
 *
 * 2D concentric rings showing Loop 3 progress:
 * - Center: Overall quality score
 * - Ring 1: Audit results (theater/production/quality)
 * - Ring 2: GitHub setup status
 * - Ring 3: CI/CD generation status
 * - Ring 4: Documentation cleanup status
 * - Ring 5: Export status
 *
 * Week 12 Day 1 Implementation
 */

'use client';

import { useState } from 'react';

interface Loop3State {
  status: string;
  currentStep: 'audit' | 'github' | 'cicd' | 'docs' | 'export' | 'complete';
  auditResults: {
    theater: { passed: number; failed: number; total: number };
    production: { passed: number; failed: number; total: number };
    quality: { passed: number; failed: number; total: number };
    overallScore: number;
  };
  github?: { repoName: string; visibility: string };
  cicd?: { enabled: boolean; workflowGenerated: boolean };
  docs?: { filesScanned: number; outdatedDocs: number; cleanupComplete: boolean };
  export?: { method: string; path?: string };
}

interface Loop3VisualizerProps {
  projectId: string;
  state: Loop3State | null;
}

export function Loop3Visualizer({ state }: Loop3VisualizerProps) {
  const [activeRing, setActiveRing] = useState<number | null>(null);

  if (!state) {
    return (
      <div className="flex items-center justify-center h-96">
        <p className="text-gray-500">Loading Loop 3 visualization...</p>
      </div>
    );
  }

  const rings = getRings(state);

  return (
    <div className="relative w-full h-96 flex items-center justify-center">
      {/* Center: Overall Quality Score */}
      <div className="absolute z-10 flex flex-col items-center">
        <div
          className={`
            w-24 h-24 rounded-full flex items-center justify-center
            ${getScoreColor(state.auditResults.overallScore)}
            shadow-lg
          `}
        >
          <span className="text-3xl font-bold text-white">
            {state.auditResults.overallScore}%
          </span>
        </div>
        <p className="mt-2 text-sm font-medium">Quality Score</p>
      </div>

      {/* Concentric Rings */}
      <svg className="w-full h-full" viewBox="0 0 400 400">
        {rings.map((ring, index) => (
          <g
            key={index}
            onMouseEnter={() => setActiveRing(index)}
            onMouseLeave={() => setActiveRing(null)}
          >
            <RingSegment
              ring={ring}
              isActive={activeRing === index}
            />
          </g>
        ))}
      </svg>

      {/* Ring Labels */}
      <div className="absolute bottom-4 left-4 right-4">
        <RingLegend rings={rings} activeRing={activeRing} />
      </div>
    </div>
  );
}

function getRings(state: Loop3State) {
  return [
    {
      name: 'Audit',
      radius: 80,
      progress: calculateAuditProgress(state.auditResults),
      color: state.currentStep === 'audit' ? '#3b82f6' : '#10b981',
      status: state.auditResults.overallScore >= 90 ? 'complete' : 'in_progress'
    },
    {
      name: 'GitHub',
      radius: 120,
      progress: state.github ? 100 : 0,
      color: state.currentStep === 'github' ? '#3b82f6' : state.github ? '#10b981' : '#6b7280',
      status: state.github ? 'complete' : state.currentStep === 'github' ? 'in_progress' : 'pending'
    },
    {
      name: 'CI/CD',
      radius: 160,
      progress: state.cicd?.workflowGenerated ? 100 : 0,
      color: state.currentStep === 'cicd' ? '#3b82f6' : state.cicd?.workflowGenerated ? '#10b981' : '#6b7280',
      status: state.cicd?.workflowGenerated ? 'complete' : state.currentStep === 'cicd' ? 'in_progress' : 'pending'
    },
    {
      name: 'Docs',
      radius: 200,
      progress: state.docs?.cleanupComplete ? 100 : state.docs ? 50 : 0,
      color: state.currentStep === 'docs' ? '#3b82f6' : state.docs?.cleanupComplete ? '#10b981' : '#6b7280',
      status: state.docs?.cleanupComplete ? 'complete' : state.currentStep === 'docs' ? 'in_progress' : 'pending'
    },
    {
      name: 'Export',
      radius: 240,
      progress: state.export ? 100 : 0,
      color: state.currentStep === 'export' ? '#3b82f6' : state.export ? '#10b981' : '#6b7280',
      status: state.export ? 'complete' : state.currentStep === 'export' ? 'in_progress' : 'pending'
    }
  ];
}

function calculateAuditProgress(auditResults: Loop3State['auditResults']): number {
  const { theater, production, quality } = auditResults;
  const total = theater.total + production.total + quality.total;
  const passed = theater.passed + production.passed + quality.passed;
  return total > 0 ? (passed / total) * 100 : 0;
}

interface RingData {
  name: string;  // Changed from 'label' to match getRings() return value
  radius: number;
  progress: number;
  color: string;
  status: string;
}

function RingSegment({
  ring,
  isActive
}: {
  ring: RingData;
  isActive: boolean;
}) {
  const cx = 200;
  const cy = 200;
  const radius = ring.radius;
  const strokeWidth = 30;
  const circumference = 2 * Math.PI * radius;
  const progressOffset = circumference - (ring.progress / 100) * circumference;

  return (
    <>
      {/* Background ring */}
      <circle
        cx={cx}
        cy={cy}
        r={radius}
        fill="none"
        stroke="#e5e7eb"
        strokeWidth={strokeWidth}
        opacity={0.3}
      />

      {/* Progress ring */}
      <circle
        cx={cx}
        cy={cy}
        r={radius}
        fill="none"
        stroke={ring.color}
        strokeWidth={strokeWidth}
        strokeDasharray={circumference}
        strokeDashoffset={progressOffset}
        strokeLinecap="round"
        transform={`rotate(-90 ${cx} ${cy})`}
        className={`transition-all duration-500 ${isActive ? 'opacity-100' : 'opacity-80'}`}
        style={{
          filter: isActive ? 'drop-shadow(0 0 8px rgba(59, 130, 246, 0.5))' : 'none'
        }}
      />
    </>
  );
}

function RingLegend({
  rings,
  activeRing
}: {
  rings: RingData[];
  activeRing: number | null;
}) {
  return (
    <div className="grid grid-cols-5 gap-2">
      {rings.map((ring, idx) => (
        <div
          key={idx}
          className={`
            flex items-center gap-2 p-2 rounded
            ${activeRing === idx ? 'bg-blue-50' : 'bg-transparent'}
          `}
        >
          <div
            className="w-3 h-3 rounded-full"
            style={{ backgroundColor: ring.color }}
          />
          <div className="flex-1 min-w-0">
            <p className="text-xs font-medium truncate">{ring.name}</p>
            <p className="text-xs text-gray-500">{Math.round(ring.progress)}%</p>
          </div>
        </div>
      ))}
    </div>
  );
}

function getScoreColor(score: number): string {
  if (score >= 90) return 'bg-green-500';
  if (score >= 70) return 'bg-yellow-500';
  if (score >= 50) return 'bg-orange-500';
  return 'bg-red-500';
}
