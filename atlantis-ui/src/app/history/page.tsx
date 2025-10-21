/**
 * Session History Page
 *
 * Browse past SPEK sessions, view results, and restore context.
 *
 * Version: 8.0.0
 * Week: 7 Day 1 (Updated Week 16 Day 1: Added AnimatedPage wrapper)
 */

import { AnimatedPage } from '@/components/layout/AnimatedPage';

export default function HistoryPage() {
  const mockSessions = [
    {
      id: '1',
      project: 'spek-v2-rebuild',
      date: '2025-10-08',
      duration: '2h 15m',
      status: 'completed',
      agents: ['queen', 'coder', 'tester', 'reviewer']
    },
    {
      id: '2',
      project: 'demo-project',
      date: '2025-10-07',
      duration: '1h 30m',
      status: 'completed',
      agents: ['queen', 'researcher', 'architect']
    },
  ];

  return (
    <AnimatedPage className="container mx-auto p-8">
      <h1 className="text-3xl font-bold mb-6">Session History</h1>

      <div className="max-w-4xl mx-auto">
        <div className="mb-4 flex gap-4">
          <input
            type="text"
            placeholder="Search sessions..."
            className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <select className="px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option>All Projects</option>
            <option>spek-v2-rebuild</option>
            <option>demo-project</option>
          </select>
        </div>

        <div className="space-y-4">
          {mockSessions.map((session) => (
            <div
              key={session.id}
              className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow"
            >
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-xl font-semibold">{session.project}</h3>
                  <p className="text-sm text-gray-600">{session.date} • {session.duration}</p>
                </div>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                  session.status === 'completed'
                    ? 'bg-green-100 text-green-800'
                    : 'bg-yellow-100 text-yellow-800'
                }`}>
                  {session.status}
                </span>
              </div>

              <div className="mb-4">
                <p className="text-sm font-medium mb-2">Agents Used:</p>
                <div className="flex gap-2 flex-wrap">
                  {session.agents.map((agent) => (
                    <span
                      key={agent}
                      className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs font-medium"
                    >
                      {agent}
                    </span>
                  ))}
                </div>
              </div>

              <div className="flex gap-2">
                <button className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm">
                  View Details
                </button>
                <button className="px-4 py-2 border border-gray-300 rounded hover:bg-gray-50 text-sm">
                  Restore Context
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </AnimatedPage>
  );
}
