/**
 * Loop 3 Page - Quality & Finalization
 *
 * Visualize Loop 3 workflow: Audit, Quality Gates, GitHub Integration.
 *
 * Version: 8.1.0 (Week 24 - Performance Optimization)
 * Week: 17 Day 1 (Updated with Honeycomb Layers 3D Visualization)
 * Week 24: Added dynamic import for 3D component (bundle size optimization)
 */

'use client';

import dynamic from 'next/dynamic';
import { AnimatedPage } from '@/components/layout/AnimatedPage';
import { RootLayout } from '@/components/layout/RootLayout';
import { LoopNavigation } from '@/components/layout/LoopNavigation';

// Dynamic import for 3D visualization (reduces initial bundle by ~280 KB)
const Loop3HoneycombLayers3D = dynamic(
  () => import('@/components/three/Loop3HoneycombLayers3D'),
  {
    ssr: false,
    loading: () => (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-orange-600 mx-auto mb-4"></div>
          <p className="text-orange-700 font-semibold">Loading 3D Honeycomb Layers...</p>
        </div>
      </div>
    ),
  }
);

export default function Loop3Page() {
  return (
    <RootLayout>
      <AnimatedPage className="min-h-screen bg-gradient-to-br from-yellow-100 via-amber-100 to-orange-200">
        <LoopNavigation />
        <div className="container mx-auto px-8 py-6">
          <div className="mb-6">
            <div className="flex items-center gap-3 mb-2">
              <span className="text-5xl">🍯</span>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-yellow-600 via-amber-600 to-orange-600 bg-clip-text text-transparent">
                Loop 3: Quality & Finalization
              </h1>
            </div>
            <p className="text-lg text-amber-800 ml-16">
              Honeycomb Quality Gates • GitHub Integration • Production Ready
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
            <div className="bg-white/95 backdrop-blur rounded-xl shadow-lg p-6 border-2 border-red-400 hover:shadow-xl transition-shadow">
              <div className="flex items-center gap-2 mb-3">
                <span className="text-3xl">🔍</span>
                <h3 className="text-xl font-bold text-orange-900">Audit Phase</h3>
              </div>
              <p className="text-sm text-orange-700">
                Comprehensive code review, quality validation, compliance checking
              </p>
            </div>

            <div className="bg-white/95 backdrop-blur rounded-xl shadow-lg p-6 border-2 border-amber-400 hover:shadow-xl transition-shadow">
              <div className="flex items-center gap-2 mb-3">
                <span className="text-3xl">✅</span>
                <h3 className="text-xl font-bold text-orange-900">Quality Gates</h3>
              </div>
              <p className="text-sm text-orange-700">
                NASA Rule 10 compliance, test coverage, security validation
              </p>
            </div>

            <div className="bg-white/95 backdrop-blur rounded-xl shadow-lg p-6 border-2 border-green-400 hover:shadow-xl transition-shadow">
              <div className="flex items-center gap-2 mb-3">
                <span className="text-3xl">🚀</span>
                <h3 className="text-xl font-bold text-orange-900">GitHub Wizard</h3>
              </div>
              <p className="text-sm text-orange-700">
                Automated PR creation, commit management, deployment workflow
              </p>
            </div>
          </div>

          <div className="bg-white/95 backdrop-blur rounded-2xl shadow-2xl p-6 min-h-[800px] border-2 border-amber-400">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <span className="text-3xl">📊</span>
                <h2 className="text-2xl font-bold text-amber-900">Quality Dashboard</h2>
              </div>
              <div className="flex items-center gap-2">
                <span className="px-4 py-2 bg-green-100 text-green-800 rounded-full text-sm font-semibold">
                  ✓ 99.0% NASA Compliance
                </span>
                <span className="px-4 py-2 bg-amber-100 text-amber-800 rounded-full text-sm font-semibold">
                  Loop 3 Active
                </span>
              </div>
            </div>
            <div className="border-2 border-amber-200 rounded-xl h-[700px] bg-gradient-to-b from-amber-100 to-yellow-100 overflow-hidden shadow-inner">
              <Loop3HoneycombLayers3D />
            </div>
          </div>

          {/* Hexagonal Pattern Overlay (subtle) */}
          <div className="fixed inset-0 pointer-events-none opacity-5">
            <div className="absolute inset-0" style={{
              backgroundImage: `url("data:image/svg+xml,%3Csvg width='80' height='80' xmlns='http://www.w3.org/2000/svg'%3E%3Cpolygon points='40,5 70,25 70,55 40,75 10,55 10,25' fill='none' stroke='%23F59E0B' stroke-width='2'/%3E%3C/svg%3E")`,
              backgroundSize: '80px 80px'
            }} />
          </div>
        </div>
      </AnimatedPage>
    </RootLayout>
  );
}
