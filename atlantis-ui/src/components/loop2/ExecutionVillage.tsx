/**
 * Loop 2 Execution Village - Princess Hive Delegation Visualizer
 *
 * Displays task phases, Princess agents, and real-time execution status
 *
 * Week 9 - Loop 2 Frontend Implementation
 */

'use client';

import { useEffect, useState } from 'react';
import { trpc } from '@/lib/trpc/client';

interface PrincessAgent {
  id: string;
  name: string;
  droneAgents: string[];
  status: 'idle' | 'busy' | 'error';
  currentTask?: string;
}

interface ExecutionVillageProps {
  projectId: string;
}

export function ExecutionVillage({ projectId }: ExecutionVillageProps) {
  const [princesses, setPrincesses] = useState<PrincessAgent[]>([]);

  const { data: princessesData } = trpc.loop2.getAllPrincesses.useQuery(
    undefined,
    { refetchInterval: 2000 }
  );

  const { data: phaseData } = trpc.loop2.getPhaseProgress.useQuery(
    { projectId },
    { refetchInterval: 2000 }
  );

  useEffect(() => {
    if (princessesData) {
      setPrincesses(princessesData);
    }
  }, [princessesData]);

  return (
    <div className="space-y-6">
      {/* Phase Progress */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold mb-4">Loop 2: Execution Village</h2>

        {phaseData && (
          <div className="mb-6">
            <div className="flex justify-between text-sm text-gray-600 mb-2">
              <span>Overall Progress</span>
              <span>{phaseData.overallProgress}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className="bg-blue-600 h-3 rounded-full transition-all duration-500"
                style={{ width: `${phaseData.overallProgress}%` }}
              />
            </div>
          </div>
        )}

        {/* Phases */}
        {phaseData?.phases && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            {phaseData.phases.map((phase) => (
              <div
                key={phase.id}
                className={`p-4 rounded-lg border-2 ${
                  phase.status === 'completed'
                    ? 'border-green-500 bg-green-50'
                    : phase.status === 'in_progress'
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-300 bg-gray-50'
                }`}
              >
                <h3 className="font-semibold mb-2">{phase.name}</h3>
                <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                  <div
                    className={`h-2 rounded-full ${
                      phase.status === 'completed'
                        ? 'bg-green-500'
                        : phase.status === 'in_progress'
                        ? 'bg-blue-500'
                        : 'bg-gray-400'
                    }`}
                    style={{ width: `${phase.progress}%` }}
                  />
                </div>
                <p className="text-xs text-gray-600">{phase.progress}% complete</p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Princess Agents */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Princess Agents</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {princesses.map((princess) => (
            <div
              key={princess.id}
              className="border rounded-lg p-4"
            >
              <div className="flex items-center justify-between mb-3">
                <h4 className="font-semibold">{princess.name}</h4>
                <span
                  className={`px-2 py-1 rounded text-xs font-semibold ${
                    princess.status === 'idle'
                      ? 'bg-gray-200 text-gray-700'
                      : princess.status === 'busy'
                      ? 'bg-blue-200 text-blue-700'
                      : 'bg-red-200 text-red-700'
                  }`}
                >
                  {princess.status}
                </span>
              </div>

              <div className="text-sm text-gray-600 mb-2">
                <strong>Drones:</strong> {princess.droneAgents.join(', ')}
              </div>

              {princess.currentTask && (
                <div className="text-xs text-blue-600">
                  Current Task: {princess.currentTask}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Task Flow Visualization (placeholder) */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Task Delegation Flow</h3>
        <div className="border rounded-lg p-4 h-64 bg-gray-50 flex items-center justify-center">
          <p className="text-gray-400">3D village visualization coming in Week 13-14...</p>
        </div>
      </div>
    </div>
  );
}
