/**
 * Select Existing Project Page
 *
 * Browse and select from existing SPEK projects.
 *
 * Version: 8.0.0
 * Week: 7 Day 1 (Updated Week 16 Day 1: Added AnimatedPage wrapper)
 */

import { AnimatedPage } from '@/components/layout/AnimatedPage';

export default function SelectProjectPage() {
  const mockProjects = [
    { id: '1', name: 'spek-v2-rebuild', path: '/Users/dev/spek-v2-rebuild', lastModified: '2025-10-08' },
    { id: '2', name: 'demo-project', path: '/Users/dev/demo-project', lastModified: '2025-10-07' },
  ];

  return (
    <AnimatedPage className="container mx-auto p-8">
      <h1 className="text-3xl font-bold mb-6">Select Existing Project</h1>

      <div className="max-w-4xl mx-auto">
        <div className="mb-4">
          <input
            type="text"
            placeholder="Search projects..."
            className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="space-y-4">
          {mockProjects.map((project) => (
            <div
              key={project.id}
              className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow cursor-pointer"
            >
              <h3 className="text-xl font-semibold mb-2">{project.name}</h3>
              <p className="text-sm text-gray-600 mb-1">{project.path}</p>
              <p className="text-xs text-gray-400">Last modified: {project.lastModified}</p>
            </div>
          ))}
        </div>
      </div>
    </AnimatedPage>
  );
}
