/**
 * Project Dashboard Component
 *
 * Advanced project dashboard with metrics and visualizations.
 *
 * Version: 8.0.0
 * Week: 7 Day 5
 */

'use client';

import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';

export function ProjectDashboard() {
  const metrics = [
    { label: 'Active Agents', value: '22', change: '+3', trend: 'up' },
    { label: 'Tasks Completed', value: '156', change: '+12', trend: 'up' },
    { label: 'Code Quality', value: '96%', change: '+2%', trend: 'up' },
    { label: 'Test Coverage', value: '82%', change: '-1%', trend: 'down' }
  ];

  const recentActivity = [
    { agent: 'queen', action: 'Task decomposition completed', time: '2 min ago', status: 'success' },
    { agent: 'coder', action: 'Implemented feature X', time: '5 min ago', status: 'success' },
    { agent: 'tester', action: 'Running test suite', time: '8 min ago', status: 'in_progress' },
    { agent: 'reviewer', action: 'Code review in progress', time: '10 min ago', status: 'in_progress' }
  ];

  return (
    <div className="space-y-6">
      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {metrics.map((metric, i) => (
          <Card key={i} variant="elevated">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600">{metric.label}</span>
              <Badge variant={metric.trend === 'up' ? 'success' : 'warning'} size="sm">
                {metric.change}
              </Badge>
            </div>
            <p className="text-3xl font-bold text-gray-900">{metric.value}</p>
          </Card>
        ))}
      </div>

      {/* Recent Activity */}
      <Card variant="bordered">
        <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>
        <div className="space-y-3">
          {recentActivity.map((activity, i) => (
            <div key={i} className="flex items-center justify-between py-2 border-b last:border-0">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <Badge variant="info" size="sm">{activity.agent}</Badge>
                  <span className="text-sm text-gray-900">{activity.action}</span>
                </div>
                <p className="text-xs text-gray-500">{activity.time}</p>
              </div>
              <Badge
                variant={activity.status === 'success' ? 'success' : 'warning'}
                size="sm"
              >
                {activity.status}
              </Badge>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
