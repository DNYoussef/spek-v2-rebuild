/**
 * Loop Navigation Component
 *
 * Navigation bar for switching between Loop 1, 2, and 3 pages
 */

'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

export function LoopNavigation() {
  const pathname = usePathname();

  const links = [
    { href: '/', label: 'Home' },
    { href: '/loop1', label: 'Loop 1: Planning' },
    { href: '/loop2', label: 'Loop 2: Execution' },
    { href: '/loop3', label: 'Loop 3: Quality' },
  ];

  return (
    <nav className="bg-gradient-to-r from-amber-500 to-yellow-400 shadow-lg mb-6">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex space-x-4">
            {links.map((link) => {
              const isActive = pathname === link.href;
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className={`px-4 py-2 rounded-lg font-semibold transition-all duration-200 ${
                    isActive
                      ? 'bg-white text-amber-600 shadow-md'
                      : 'text-white hover:bg-amber-600 hover:shadow-md'
                  }`}
                >
                  {link.label}
                </Link>
              );
            })}
          </div>
          <div className="text-white font-bold text-lg">
            🐝 SPEK Platform v2
          </div>
        </div>
      </div>
    </nav>
  );
}
