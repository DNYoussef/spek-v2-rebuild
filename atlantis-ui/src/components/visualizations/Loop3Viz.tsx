/**
 * Loop 3 Visualization - Quality & Finalization
 *
 * 2D quality gates and GitHub workflow visualization.
 *
 * Version: 8.0.0
 * Week: 7 Day 3
 */

'use client';

export function Loop3Viz() {
  const gates = [
    { id: 1, name: 'Audit', status: 'passed', y: 20 },
    { id: 2, name: 'Tests', status: 'passed', y: 40 },
    { id: 3, name: 'Quality', status: 'in_progress', y: 60 },
    { id: 4, name: 'Deploy', status: 'pending', y: 80 }
  ];

  const getColor = (status: string) => {
    switch (status) {
      case 'passed': return '#10B981';
      case 'in_progress': return '#3B82F6';
      case 'pending': return '#9CA3AF';
      default: return '#9CA3AF';
    }
  };

  return (
    <div className="relative w-full h-full bg-gray-50 rounded-lg border p-8">
      <svg className="w-full h-full" viewBox="0 0 100 100">
        {/* Vertical pipeline */}
        <line x1="50" y1="10" x2="50" y2="90" stroke="#E5E7EB" strokeWidth="1" />

        {/* Gates */}
        {gates.map(gate => (
          <g key={gate.id}>
            <rect
              x="35"
              y={gate.y - 5}
              width="30"
              height="10"
              fill={getColor(gate.status)}
              rx="2"
              className="transition-all hover:opacity-80"
            />
            <text
              x="50"
              y={gate.y + 1}
              textAnchor="middle"
              className="text-xs font-medium"
              fill="white"
            >
              {gate.name}
            </text>
          </g>
        ))}

        {/* Status indicators */}
        {gates.map(gate => (
          <circle
            key={`ind-${gate.id}`}
            cx="75"
            cy={gate.y}
            r="3"
            fill={getColor(gate.status)}
          />
        ))}
      </svg>
    </div>
  );
}
