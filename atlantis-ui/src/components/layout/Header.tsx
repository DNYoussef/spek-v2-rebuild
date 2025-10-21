/**
 * Header Component
 *
 * Top navigation bar for SPEK Atlantis UI with golden bee theme.
 *
 * Version: 8.1.0
 * Week: 25 (Bee Hive theme implementation)
 */

'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

export function Header() {
  const pathname = usePathname();

  const isActive = (path: string) => pathname === path;

  return (
    <header className="bg-gradient-to-r from-amber-500 via-yellow-400 to-amber-500 shadow-lg border-b-2 border-amber-600">
      <div className="container mx-auto px-8 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-3 group">
            <div className="w-10 h-10 bg-white rounded-lg flex items-center justify-center shadow-md group-hover:scale-110 transition-transform">
              <span className="text-3xl">🐝</span>
            </div>
            <div>
              <span className="text-2xl font-bold text-white">SPEK Atlantis</span>
              <p className="text-xs text-amber-100">AI Agent Coordination</p>
            </div>
          </Link>

          {/* Navigation */}
          <nav className="flex items-center gap-2">
            <Link
              href="/"
              className={`px-4 py-2 rounded-lg font-semibold transition-all ${
                isActive('/')
                  ? 'bg-white text-amber-600 shadow-md'
                  : 'text-white hover:bg-amber-600 hover:shadow-md'
              }`}
            >
              🏠 Home
            </Link>
            <Link
              href="/project/new"
              className={`px-4 py-2 rounded-lg font-semibold transition-all ${
                isActive('/project/new')
                  ? 'bg-white text-amber-600 shadow-md'
                  : 'text-white hover:bg-amber-600 hover:shadow-md'
              }`}
            >
              ✨ New Project
            </Link>
            <Link
              href="/project/select"
              className={`px-4 py-2 rounded-lg font-semibold transition-all ${
                isActive('/project/select')
                  ? 'bg-white text-amber-600 shadow-md'
                  : 'text-white hover:bg-amber-600 hover:shadow-md'
              }`}
            >
              📁 Projects
            </Link>
            <Link
              href="/history"
              className={`px-4 py-2 rounded-lg font-semibold transition-all ${
                isActive('/history')
                  ? 'bg-white text-amber-600 shadow-md'
                  : 'text-white hover:bg-amber-600 hover:shadow-md'
              }`}
            >
              📜 History
            </Link>
            <Link
              href="/settings"
              className={`px-4 py-2 rounded-lg font-semibold transition-all ${
                isActive('/settings')
                  ? 'bg-white text-amber-600 shadow-md'
                  : 'text-white hover:bg-amber-600 hover:shadow-md'
              }`}
            >
              ⚙️ Settings
            </Link>
            <Link
              href="/help"
              className={`px-4 py-2 rounded-lg font-semibold transition-all ${
                isActive('/help')
                  ? 'bg-white text-amber-600 shadow-md'
                  : 'text-white hover:bg-amber-600 hover:shadow-md'
              }`}
            >
              ❓ Help
            </Link>
          </nav>

          {/* Status Indicator */}
          <div className="flex items-center gap-2 bg-white/20 px-4 py-2 rounded-lg backdrop-blur">
            <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></div>
            <span className="text-sm font-semibold text-white">Connected</span>
          </div>
        </div>
      </div>
    </header>
  );
}
