/**
 * Help & Documentation Page
 *
 * User guides, API documentation, and platform tutorials.
 *
 * Version: 8.0.0
 * Week: 7 Day 1 (Updated Week 16 Day 1: Added AnimatedPage wrapper)
 */

import { AnimatedPage } from '@/components/layout/AnimatedPage';

export default function HelpPage() {
  const helpSections = [
    {
      title: 'Getting Started',
      topics: [
        'Creating Your First Project',
        'Understanding the Three Loops',
        'Working with Monarch Chat',
        'Agent Overview'
      ]
    },
    {
      title: 'Loop Workflows',
      topics: [
        'Loop 1: Research & Planning',
        'Loop 2: Execution with Princess Hive',
        'Loop 3: Quality & Finalization',
        'MECE Analysis Methodology'
      ]
    },
    {
      title: 'Advanced Features',
      topics: [
        'DSPy Optimization',
        '3D Visualizations',
        'Context DNA Storage',
        'WebSocket Real-time Updates'
      ]
    },
    {
      title: 'Quality & Compliance',
      topics: [
        'NASA Rule 10 Guidelines',
        'Test Coverage Requirements',
        'Security Best Practices',
        'Code Review Process'
      ]
    }
  ];

  return (
    <AnimatedPage className="container mx-auto p-8">
      <h1 className="text-3xl font-bold mb-6">Help & Documentation</h1>

      <div className="max-w-4xl mx-auto">
        <div className="mb-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-2 text-blue-900">Welcome to SPEK Atlantis</h2>
          <p className="text-blue-800">
            SPEK is an AI-powered agent coordination platform that uses a three-loop methodology
            to guide you from research to production-ready code.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {helpSections.map((section) => (
            <div key={section.title} className="bg-white rounded-lg shadow p-6">
              <h3 className="text-xl font-semibold mb-4">{section.title}</h3>
              <ul className="space-y-2">
                {section.topics.map((topic) => (
                  <li key={topic}>
                    <a
                      href="#"
                      className="text-blue-600 hover:text-blue-800 hover:underline text-sm"
                    >
                      {topic}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-8 bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Quick Reference</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div>
              <h4 className="font-semibold mb-2">22 Specialized Agents</h4>
              <p className="text-gray-600">
                Queen, 3 Princesses, 5 Core agents, 14 Specialized agents
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-2">Quality Gates</h4>
              <p className="text-gray-600">
                ≥80% test coverage, ≥92% NASA compliance, ≤60 LOC/function
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-2">Performance Targets</h4>
              <p className="text-gray-600">
                &lt;100ms coordination, &lt;200ms context search, &lt;20s sandbox
              </p>
            </div>
          </div>
        </div>

        <div className="mt-8 text-center">
          <a
            href="https://github.com/yourusername/spek-v2"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-block px-6 py-3 bg-gray-800 text-white rounded-lg hover:bg-gray-900 font-semibold"
          >
            View Full Documentation on GitHub
          </a>
        </div>
      </div>
    </AnimatedPage>
  );
}
