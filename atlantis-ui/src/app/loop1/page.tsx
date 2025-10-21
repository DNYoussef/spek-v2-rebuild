/**
 * Loop 1 Page - Research & Planning
 *
 * Visualize Loop 1 workflow: Research, Specification, Pre-mortem Analysis.
 *
 * Version: 8.1.0 (Week 24 - Performance Optimization)
 * Week: 17 Day 1 (Updated with Flower Garden 3D Visualization)
 * Week 24: Added dynamic import for 3D component (bundle size optimization)
 */

'use client';

import dynamic from 'next/dynamic';
import { AnimatedPage } from '@/components/layout/AnimatedPage';
import { RootLayout } from '@/components/layout/RootLayout';
import { LoopNavigation } from '@/components/layout/LoopNavigation';

// Dynamic import for 3D visualization (reduces initial bundle size)
const Loop1FlowerGarden3D = dynamic(
  () => import('@/components/three/Loop1FlowerGarden3D'),
  {
    ssr: false,
    loading: () => (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-green-600 mx-auto mb-4"></div>
          <p className="text-green-700 font-semibold">Loading 3D Flower Garden...</p>
        </div>
      </div>
    ),
  }
);

export default function Loop1Page() {
  return (
    <RootLayout>
      <AnimatedPage className="min-h-screen bg-gradient-to-br from-green-50 via-emerald-50 to-teal-50">
        <LoopNavigation />
        <div className="container mx-auto px-8 py-6">
          <div className="mb-6">
            <div className="flex items-center gap-3 mb-2">
              <span className="text-5xl">🌸</span>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-green-600 via-emerald-600 to-teal-600 bg-clip-text text-transparent">
                Loop 1: Research & Planning
              </h1>
            </div>
            <p className="text-lg text-green-700 ml-16">
              Flower Garden • SPARC Methodology • Pre-mortem Analysis
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
            <div className="bg-white/90 backdrop-blur rounded-xl shadow-lg p-6 border-l-4 border-pink-400 hover:shadow-xl transition-shadow">
              <div className="flex items-center gap-2 mb-3">
                <span className="text-3xl">🔍</span>
                <h3 className="text-xl font-bold text-green-900">Research Phase</h3>
              </div>
              <p className="text-sm text-green-700">
                Gather requirements, analyze existing solutions, identify constraints
              </p>
            </div>

            <div className="bg-white/90 backdrop-blur rounded-xl shadow-lg p-6 border-l-4 border-purple-400 hover:shadow-xl transition-shadow">
              <div className="flex items-center gap-2 mb-3">
                <span className="text-3xl">📝</span>
                <h3 className="text-xl font-bold text-green-900">Specification Phase</h3>
              </div>
              <p className="text-sm text-green-700">
                Define requirements, create detailed specifications, establish acceptance criteria
              </p>
            </div>

            <div className="bg-white/90 backdrop-blur rounded-xl shadow-lg p-6 border-l-4 border-red-400 hover:shadow-xl transition-shadow">
              <div className="flex items-center gap-2 mb-3">
                <span className="text-3xl">⚠️</span>
                <h3 className="text-xl font-bold text-green-900">Pre-mortem Phase</h3>
              </div>
              <p className="text-sm text-green-700">
                Identify risks, analyze failure scenarios, create mitigation strategies
              </p>
            </div>
          </div>

          <div className="bg-white/95 backdrop-blur rounded-2xl shadow-2xl p-6 min-h-[800px] border-2 border-green-300">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <span className="text-3xl">🌺</span>
                <h2 className="text-2xl font-bold text-green-900">Flower Garden Visualization</h2>
              </div>
              <span className="px-4 py-2 bg-green-100 text-green-800 rounded-full text-sm font-semibold">
                Loop 1 Active
              </span>
            </div>
            <div className="border-2 border-green-200 rounded-xl h-[700px] bg-gradient-to-b from-sky-100 to-green-50 overflow-hidden shadow-inner">
              <Loop1FlowerGarden3D />
            </div>
          </div>
        </div>
      </AnimatedPage>
    </RootLayout>
  );
}
