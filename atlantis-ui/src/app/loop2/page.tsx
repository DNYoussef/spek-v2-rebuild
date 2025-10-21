/**
 * Loop 2 Page - Execution
 *
 * Visualize Loop 2 workflow: MECE Analysis, Princess Hive Model, Agent Execution.
 *
 * Version: 8.1.0 (Week 24 - Performance Optimization)
 * Week: 17 Day 1 (Updated with Beehive Village 3D Visualization)
 * Week 24: Added dynamic import for 3D component (bundle size optimization)
 */

'use client';

import dynamic from 'next/dynamic';
import { AnimatedPage } from '@/components/layout/AnimatedPage';
import { RootLayout } from '@/components/layout/RootLayout';
import { LoopNavigation } from '@/components/layout/LoopNavigation';

// Dynamic import for 3D visualization (reduces initial bundle size)
const Loop2BeehiveVillage3D = dynamic(
  () => import('@/components/three/Loop2BeehiveVillage3D'),
  {
    ssr: false,
    loading: () => (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-amber-600 mx-auto mb-4"></div>
          <p className="text-amber-700 font-semibold">Loading 3D Beehive Village...</p>
        </div>
      </div>
    ),
  }
);

export default function Loop2Page() {
  return (
    <RootLayout>
      <AnimatedPage className="min-h-screen bg-gradient-to-br from-amber-100 via-yellow-100 to-orange-100">
        <LoopNavigation />
        <div className="container mx-auto px-8 py-6">
          <div className="mb-6">
            <div className="flex items-center gap-3 mb-2">
              <span className="text-5xl">🐝</span>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-amber-600 via-yellow-600 to-orange-600 bg-clip-text text-transparent">
                Loop 2: Execution Village
              </h1>
            </div>
            <p className="text-lg text-amber-800 ml-16">
              Princess Hive • MECE Task Delegation • Real-time Agent Coordination
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
            <div className="bg-white/90 backdrop-blur rounded-xl shadow-lg p-6 border-2 border-amber-300 hover:shadow-xl transition-shadow">
              <div className="flex items-center gap-2 mb-3">
                <span className="text-3xl">📊</span>
                <h3 className="text-xl font-bold text-amber-900">MECE Analysis</h3>
              </div>
              <p className="text-sm text-amber-700">
                Mutually Exclusive, Collectively Exhaustive task decomposition
              </p>
            </div>

            <div className="bg-white/90 backdrop-blur rounded-xl shadow-lg p-6 border-2 border-yellow-300 hover:shadow-xl transition-shadow">
              <div className="flex items-center gap-2 mb-3">
                <span className="text-3xl">👑</span>
                <h3 className="text-xl font-bold text-amber-900">Princess Hive Model</h3>
              </div>
              <p className="text-sm text-amber-700">
                Queen → Princess → Drone delegation hierarchy for parallel execution
              </p>
            </div>

            <div className="bg-white/90 backdrop-blur rounded-xl shadow-lg p-6 border-2 border-orange-300 hover:shadow-xl transition-shadow">
              <div className="flex items-center gap-2 mb-3">
                <span className="text-3xl">⚡</span>
                <h3 className="text-xl font-bold text-amber-900">Agent Execution</h3>
              </div>
              <p className="text-sm text-amber-700">
                22 specialized agents execute tasks with real-time progress tracking
              </p>
            </div>
          </div>

          <div className="bg-white/95 backdrop-blur rounded-2xl shadow-2xl p-6 min-h-[800px] border-2 border-amber-300">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <span className="text-3xl">🏘️</span>
                <h2 className="text-2xl font-bold text-amber-900">Princess Hive Visualization</h2>
              </div>
              <span className="px-4 py-2 bg-amber-100 text-amber-800 rounded-full text-sm font-semibold animate-pulse">
                Loop 2 Active
              </span>
            </div>
            <div className="border-2 border-amber-200 rounded-xl h-[700px] bg-gradient-to-b from-amber-50 to-yellow-50 overflow-hidden shadow-inner">
              <Loop2BeehiveVillage3D />
            </div>
          </div>

          {/* Honeycomb Pattern Overlay (subtle) */}
          <div className="fixed inset-0 pointer-events-none opacity-5">
            <div className="absolute inset-0" style={{
              backgroundImage: `url("data:image/svg+xml,%3Csvg width='100' height='100' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M25,10 L40,2 L55,10 L55,26 L40,34 L25,26 Z' fill='none' stroke='%23F59E0B' stroke-width='2'/%3E%3C/svg%3E")`,
              backgroundSize: '100px 100px'
            }} />
          </div>
        </div>
      </AnimatedPage>
    </RootLayout>
  );
}
