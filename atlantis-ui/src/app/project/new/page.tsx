/**
 * New Project Page
 *
 * Create a new SPEK project with configuration wizard.
 *
 * Version: 8.0.0
 * Week: 7 Day 1 (Updated Week 16 Day 1: Added AnimatedPage wrapper)
 */

import { AnimatedPage } from '@/components/layout/AnimatedPage';

export default function NewProjectPage() {
  return (
    <AnimatedPage className="container mx-auto p-8">
      <h1 className="text-3xl font-bold mb-6">Create New Project</h1>

      <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-lg p-6">
        <form className="space-y-6">
          <div>
            <label htmlFor="projectName" className="block text-sm font-medium mb-2">
              Project Name
            </label>
            <input
              id="projectName"
              type="text"
              placeholder="my-awesome-project"
              className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label htmlFor="projectPath" className="block text-sm font-medium mb-2">
              Project Path
            </label>
            <input
              id="projectPath"
              type="text"
              placeholder="/path/to/project"
              className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label htmlFor="description" className="block text-sm font-medium mb-2">
              Description
            </label>
            <textarea
              id="description"
              rows={4}
              placeholder="Brief project description..."
              className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <button
            type="submit"
            className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold"
          >
            Create Project
          </button>
        </form>
      </div>
    </AnimatedPage>
  );
}
