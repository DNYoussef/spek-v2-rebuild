/**
 * Loop 1 Visualization - Research & Planning
 *
 * 2D flowchart visualization for Loop 1 workflow.
 *
 * Version: 8.0.0
 * Week: 7 Day 3
 */

'use client';

export function Loop1Viz() {
  const phases = [
    { id: 1, name: 'Research', status: 'completed', x: 50, y: 20 },
    { id: 2, name: 'Specification', status: 'completed', x: 50, y: 50 },
    { id: 3, name: 'Pre-mortem', status: 'in_progress', x: 50, y: 80 }
  ];

  const connections = [
    { from: 1, to: 2 },
    { from: 2, to: 3 }
  ];

  return (
    <div className="relative w-full h-full bg-gray-50 rounded-lg border p-8">
      <svg className="w-full h-full" viewBox="0 0 100 100">
        {/* Connections */}
        {connections.map((conn, i) => {
          const from = phases.find(p => p.id === conn.from)!;
          const to = phases.find(p => p.id === conn.to)!;
          return (
            <line
              key={i}
              x1={from.x}
              y1={from.y}
              x2={to.x}
              y2={to.y}
              stroke="#3B82F6"
              strokeWidth="0.5"
              strokeDasharray="2,1"
            />
          );
        })}

        {/* Phase Nodes */}
        {phases.map(phase => (
          <g key={phase.id}>
            <circle
              cx={phase.x}
              cy={phase.y}
              r="8"
              fill={phase.status === 'completed' ? '#10B981' : '#3B82F6'}
              className="transition-all hover:scale-110"
            />
            <text
              x={phase.x}
              y={phase.y + 12}
              textAnchor="middle"
              className="text-xs font-medium"
              fill="#1F2937"
            >
              {phase.name}
            </text>
          </g>
        ))}
      </svg>
    </div>
  );
}
