/**
 * Sidebar Component
 *
 * Side navigation for loop workflows and quick access with warm hive theme.
 *
 * Version: 8.1.0
 * Week: 25 (Bee Hive theme implementation)
 */

'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

export function Sidebar() {
  const pathname = usePathname();

  const isActive = (path: string) => pathname === path;

  // TODO: Connect to WebSocket for real-time agent status
  // TODO: Get project context from global state (new vs existing, folder path)

  return (
    <aside className="w-64 bg-gradient-to-b from-amber-50 to-yellow-50 border-r-2 border-amber-200 min-h-screen p-6">
      {/* Workflow Loops */}
      <div className="mb-8">
        <h3 className="text-sm font-bold text-amber-800 uppercase mb-3 flex items-center gap-2">
          <span>🔄</span> Workflow Loops
        </h3>
        <nav className="space-y-2">
          <Link
            href="/loop1"
            className={`block px-4 py-3 rounded-lg text-sm font-semibold transition-all ${
              isActive('/loop1')
                ? 'bg-gradient-to-r from-green-400 to-emerald-400 text-white shadow-lg scale-105'
                : 'text-amber-900 hover:bg-amber-100 border border-transparent hover:border-amber-300'
            }`}
          >
            <div className="flex items-center gap-2">
              <span>🌸</span>
              <div>
                <div>Loop 1: Research</div>
                <div className="text-xs opacity-75">Planning & Analysis</div>
              </div>
            </div>
          </Link>
          <Link
            href="/loop2"
            className={`block px-4 py-3 rounded-lg text-sm font-semibold transition-all ${
              isActive('/loop2')
                ? 'bg-gradient-to-r from-amber-500 to-orange-500 text-white shadow-lg scale-105'
                : 'text-amber-900 hover:bg-amber-100 border border-transparent hover:border-amber-300'
            }`}
          >
            <div className="flex items-center gap-2">
              <span>🐝</span>
              <div>
                <div>Loop 2: Execution</div>
                <div className="text-xs opacity-75">Princess Hive</div>
              </div>
            </div>
          </Link>
          <Link
            href="/loop3"
            className={`block px-4 py-3 rounded-lg text-sm font-semibold transition-all ${
              isActive('/loop3')
                ? 'bg-gradient-to-r from-yellow-500 to-amber-500 text-white shadow-lg scale-105'
                : 'text-amber-900 hover:bg-amber-100 border border-transparent hover:border-amber-300'
            }`}
          >
            <div className="flex items-center gap-2">
              <span>🍯</span>
              <div>
                <div>Loop 3: Quality</div>
                <div className="text-xs opacity-75">Finalization</div>
              </div>
            </div>
          </Link>
        </nav>
      </div>

      {/* Active Agents */}
      <div className="mb-8">
        <h3 className="text-sm font-bold text-amber-800 uppercase mb-3 flex items-center gap-2">
          <span>🐝</span> Active Agents
        </h3>
        <div className="space-y-2">
          {/* Queen Agent */}
          <div className="px-4 py-3 bg-white/80 backdrop-blur rounded-lg border-2 border-amber-200 shadow-sm">
            <div className="flex items-center justify-between mb-1">
              <div className="flex items-center gap-2">
                <span>👑</span>
                <span className="text-sm font-bold text-amber-900">Queen</span>
              </div>
              <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
            </div>
            <p className="text-xs text-amber-700">Orchestrating workflow</p>
          </div>

          {/* TODO: Map through real agent statuses from WebSocket */}
          {/* Placeholder agents */}
          <div className="px-3 py-2 bg-amber-50 rounded-lg border border-amber-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-xs">💼</span>
                <span className="text-xs font-semibold text-amber-800">Coder</span>
              </div>
              <div className="w-1.5 h-1.5 rounded-full bg-yellow-500"></div>
            </div>
          </div>

          <div className="px-3 py-2 bg-amber-50 rounded-lg border border-amber-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-xs">🧪</span>
                <span className="text-xs font-semibold text-amber-800">Tester</span>
              </div>
              <div className="w-1.5 h-1.5 rounded-full bg-gray-400"></div>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="bg-white/80 backdrop-blur rounded-xl p-4 border-2 border-amber-200 shadow-sm">
        <h3 className="text-sm font-bold text-amber-800 uppercase mb-3 flex items-center gap-2">
          <span>📊</span> Quick Stats
        </h3>
        <div className="space-y-3 text-sm">
          <div className="flex justify-between items-center">
            <span className="text-amber-700">Tasks</span>
            <span className="font-bold text-amber-900">0 / 0</span>
          </div>
          <div className="w-full bg-amber-100 rounded-full h-2">
            <div className="bg-gradient-to-r from-amber-500 to-orange-500 h-2 rounded-full" style={{ width: '0%' }}></div>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-amber-700">Progress</span>
            <span className="font-bold text-amber-900">0%</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-amber-700">Quality</span>
            <span className="font-bold text-green-600 flex items-center gap-1">
              <span>✓</span> Ready
            </span>
          </div>
        </div>
      </div>

      {/* Project Context Indicator (TODO: Connect to global state) */}
      <div className="mt-4 px-3 py-2 bg-amber-100 rounded-lg border border-amber-300 text-xs text-amber-800">
        <div className="font-semibold mb-1">📁 Project Context</div>
        <div className="opacity-75">No project selected</div>
        {/* TODO: Show project type (new/existing) and folder path */}
      </div>
    </aside>
  );
}
