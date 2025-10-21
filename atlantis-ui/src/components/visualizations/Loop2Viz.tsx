/**
 * Loop 2 Visualization - Execution (Princess Hive)
 *
 * 2D hierarchy visualization for Princess Hive Model.
 *
 * Version: 8.0.0
 * Week: 7 Day 3
 */

'use client';

export function Loop2Viz() {
  return (
    <div className="relative w-full h-full bg-gray-50 rounded-lg border p-8">
      <svg className="w-full h-full" viewBox="0 0 100 100">
        {/* Queen at top */}
        <circle cx="50" cy="15" r="6" fill="#8B5CF6" />
        <text x="50" y="28" textAnchor="middle" className="text-xs font-bold" fill="#1F2937">
          Queen
        </text>

        {/* Lines to Princesses */}
        <line x1="50" y1="21" x2="20" y2="45" stroke="#3B82F6" strokeWidth="0.5" />
        <line x1="50" y1="21" x2="50" y2="45" stroke="#3B82F6" strokeWidth="0.5" />
        <line x1="50" y1="21" x2="80" y2="45" stroke="#3B82F6" strokeWidth="0.5" />

        {/* Princesses */}
        <circle cx="20" cy="50" r="5" fill="#EC4899" />
        <text x="20" y="62" textAnchor="middle" className="text-xs" fill="#1F2937">
          Dev
        </text>

        <circle cx="50" cy="50" r="5" fill="#EC4899" />
        <text x="50" y="62" textAnchor="middle" className="text-xs" fill="#1F2937">
          Quality
        </text>

        <circle cx="80" cy="50" r="5" fill="#EC4899" />
        <text x="80" y="62" textAnchor="middle" className="text-xs" fill="#1F2937">
          Coord
        </text>

        {/* Drone lines */}
        <line x1="20" y1="55" x2="15" y2="80" stroke="#3B82F6" strokeWidth="0.3" />
        <line x1="20" y1="55" x2="25" y2="80" stroke="#3B82F6" strokeWidth="0.3" />
        <line x1="50" y1="55" x2="45" y2="80" stroke="#3B82F6" strokeWidth="0.3" />
        <line x1="50" y1="55" x2="55" y2="80" stroke="#3B82F6" strokeWidth="0.3" />
        <line x1="80" y1="55" x2="75" y2="80" stroke="#3B82F6" strokeWidth="0.3" />
        <line x1="80" y1="55" x2="85" y2="80" stroke="#3B82F6" strokeWidth="0.3" />

        {/* Drones (smaller dots) */}
        {[15, 25, 45, 55, 75, 85].map((x, i) => (
          <circle key={i} cx={x} cy="85" r="2" fill="#10B981" />
        ))}
      </svg>
    </div>
  );
}
