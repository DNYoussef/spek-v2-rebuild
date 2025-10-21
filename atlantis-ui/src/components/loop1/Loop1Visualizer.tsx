/**
 * Loop 1 Visualizer - Research & Pre-mortem Workflow
 *
 * Displays failure rate, agent thoughts, research artifacts
 *
 * Week 9 - Loop 1 Frontend Implementation
 */

'use client';

import { useEffect, useState } from 'react';
import { trpc } from '@/lib/trpc/client';

export interface Loop1State {
  projectId: string;
  currentIteration: number;
  maxIterations: number;
  failureRateHistory: number[];
  currentFailureRate: number;
  targetFailureRate: number;
  status: 'running' | 'paused' | 'completed' | 'failed';
}

interface Loop1VisualizerProps {
  projectId: string;
}

export function Loop1Visualizer({ projectId }: Loop1VisualizerProps) {
  const [state, setState] = useState<Loop1State | null>(null);

  const { data: statusData, isLoading } = trpc.loop1.getStatus.useQuery(
    { projectId },
    { refetchInterval: 2000 } // Poll every 2 seconds
  );

  useEffect(() => {
    if (statusData) {
      setState(statusData as Loop1State);
    }
  }, [statusData]);

  if (isLoading) {
    return <div className="text-gray-500">Loading Loop 1 status...</div>;
  }

  if (!state) {
    return <div className="text-gray-500">No Loop 1 session found</div>;
  }

  const failureRateColor = state.currentFailureRate <= state.targetFailureRate
    ? 'text-green-600'
    : state.currentFailureRate <= 20
    ? 'text-yellow-600'
    : 'text-red-600';

  const progress = (state.currentIteration / state.maxIterations) * 100;

  return (
    <div className="space-y-6">
      {/* Status Header */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold">Loop 1: Research & Pre-mortem</h2>
          <div className={`px-4 py-2 rounded-full text-sm font-semibold ${
            state.status === 'completed' ? 'bg-green-100 text-green-800' :
            state.status === 'running' ? 'bg-blue-100 text-blue-800' :
            state.status === 'paused' ? 'bg-yellow-100 text-yellow-800' :
            'bg-red-100 text-red-800'
          }`}>
            {state.status.toUpperCase()}
          </div>
        </div>

        {/* Failure Rate Gauge */}
        <div className="text-center mb-4">
          <div className={`text-5xl font-bold ${failureRateColor}`}>
            {state.currentFailureRate.toFixed(1)}%
          </div>
          <div className="text-sm text-gray-600 mt-1">
            Failure Rate (Target: {state.targetFailureRate}%)
          </div>
        </div>

        {/* Iteration Counter */}
        <div className="flex items-center justify-center space-x-2 mb-4">
          <span className="text-gray-600">Iteration:</span>
          <span className="font-semibold">{state.currentIteration} / {state.maxIterations}</span>
        </div>

        {/* Progress Bar */}
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-blue-600 h-2 rounded-full transition-all duration-500"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Failure Rate History Chart */}
      {state.failureRateHistory.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Failure Rate Trend</h3>
          <div className="flex items-end space-x-2 h-40">
            {state.failureRateHistory.map((rate, index) => {
              const height = (rate / 100) * 100; // Scale to 100%
              const color = rate <= state.targetFailureRate
                ? 'bg-green-500'
                : rate <= 20
                ? 'bg-yellow-500'
                : 'bg-red-500';

              return (
                <div key={index} className="flex-1 flex flex-col items-center">
                  <div
                    className={`w-full ${color} rounded-t transition-all duration-300`}
                    style={{ height: `${height}%` }}
                  />
                  <span className="text-xs text-gray-600 mt-1">{index + 1}</span>
                </div>
              );
            })}
          </div>
          <div className="flex justify-between mt-2 text-xs text-gray-600">
            <span>Iteration</span>
            <span>Target: {state.targetFailureRate}%</span>
          </div>
        </div>
      )}

      {/* Research Artifacts (placeholder) */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Research Artifacts</h3>
        <p className="text-sm text-gray-600">
          Research results will appear here during execution...
        </p>
      </div>

      {/* Pre-mortem Report (placeholder) */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Pre-mortem Analysis</h3>
        <p className="text-sm text-gray-600">
          Failure scenarios will appear here during pre-mortem phase...
        </p>
      </div>
    </div>
  );
}
