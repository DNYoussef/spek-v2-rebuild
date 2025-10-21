/**
 * Settings Page
 *
 * Configure SPEK platform settings, agent preferences, and system options.
 *
 * Version: 8.0.0
 * Week: 7 Day 1 (Updated Week 16 Day 1: Added AnimatedPage wrapper)
 */

import { AnimatedPage } from '@/components/layout/AnimatedPage';

export default function SettingsPage() {
  return (
    <AnimatedPage className="container mx-auto p-8">
      <h1 className="text-3xl font-bold mb-6">Settings</h1>

      <div className="max-w-4xl mx-auto space-y-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">General Settings</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">
                Default Project Directory
              </label>
              <input
                type="text"
                placeholder="/Users/dev/projects"
                className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                API Endpoint
              </label>
              <input
                type="text"
                placeholder="http://localhost:3000"
                className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Agent Configuration</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Enable DSPy Optimization</span>
              <input type="checkbox" className="w-5 h-5" />
            </div>

            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Enable 3D Visualizations</span>
              <input type="checkbox" className="w-5 h-5" />
            </div>

            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Real-time Progress Updates</span>
              <input type="checkbox" className="w-5 h-5" defaultChecked />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Quality Gates</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">
                Minimum Test Coverage (%)
              </label>
              <input
                type="number"
                defaultValue={80}
                min={0}
                max={100}
                className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                Maximum Function Length (lines)
              </label>
              <input
                type="number"
                defaultValue={60}
                min={10}
                max={200}
                className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>

        <button className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold">
          Save Settings
        </button>
      </div>
    </AnimatedPage>
  );
}
