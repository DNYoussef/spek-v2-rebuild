/**
 * Pre-mortem Scenario Cards
 * Displays failure scenarios by priority (P0/P1/P2/P3)
 *
 * Week 10 Day 3 Implementation
 */

'use client';

import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';

export interface FailureScenario {
  id: string;
  priority: 'P0' | 'P1' | 'P2' | 'P3';
  description: string;
  likelihood: number; // 0-1
  impact: number; // 0-1
  prevention: string;
}

export interface PremortemScenarioCardsProps {
  scenarios: FailureScenario[];
  riskScore: number;
  isLoading?: boolean;
}

const PRIORITY_CONFIG = {
  P0: {
    label: 'Critical',
    color: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300',
    borderColor: 'border-red-500',
  },
  P1: {
    label: 'High',
    color: 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300',
    borderColor: 'border-orange-500',
  },
  P2: {
    label: 'Medium',
    color: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300',
    borderColor: 'border-yellow-500',
  },
  P3: {
    label: 'Low',
    color: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300',
    borderColor: 'border-blue-500',
  },
};

export function PremortemScenarioCards({
  scenarios,
  riskScore,
  isLoading = false,
}: PremortemScenarioCardsProps) {
  if (isLoading) {
    return (
      <div className="space-y-4">
        {[...Array(3)].map((_, i) => (
          <Card key={i} className="p-6">
            <div className="animate-pulse space-y-3">
              <div className="h-4 bg-gray-300 dark:bg-gray-700 rounded w-1/4"></div>
              <div className="h-4 bg-gray-300 dark:bg-gray-700 rounded w-3/4"></div>
              <div className="h-4 bg-gray-300 dark:bg-gray-700 rounded w-1/2"></div>
            </div>
          </Card>
        ))}
      </div>
    );
  }

  // Group scenarios by priority
  const groupedScenarios = scenarios.reduce((acc, scenario) => {
    if (!acc[scenario.priority]) acc[scenario.priority] = [];
    acc[scenario.priority].push(scenario);
    return acc;
  }, {} as Record<string, FailureScenario[]>);

  const priorities: Array<'P0' | 'P1' | 'P2' | 'P3'> = ['P0', 'P1', 'P2', 'P3'];

  return (
    <div className="space-y-6">
      {/* Risk Score Summary */}
      <Card className="p-6 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-bold text-gray-900 dark:text-white">
              Total Risk Score
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
              {scenarios.length} scenarios identified
            </p>
          </div>
          <div className="text-right">
            <div className="text-4xl font-bold text-purple-600 dark:text-purple-400">
              {riskScore.toFixed(0)}
            </div>
            <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
              Target: &lt;500
            </p>
          </div>
        </div>
      </Card>

      {/* Scenario Cards by Priority */}
      {priorities.map((priority) => {
        const priorityScenarios = groupedScenarios[priority] || [];
        if (priorityScenarios.length === 0) return null;

        const config = PRIORITY_CONFIG[priority];

        return (
          <div key={priority}>
            <div className="flex items-center gap-2 mb-3">
              <Badge className={config.color}>
                {priority} - {config.label}
              </Badge>
              <span className="text-sm text-gray-500 dark:text-gray-400">
                {priorityScenarios.length} scenario{priorityScenarios.length !== 1 ? 's' : ''}
              </span>
            </div>

            <div className="space-y-3">
              {priorityScenarios.map((scenario) => (
                <Card
                  key={scenario.id}
                  className={`p-5 border-l-4 ${config.borderColor}`}
                >
                  <div className="flex items-start justify-between mb-3">
                    <h4 className="text-base font-semibold text-gray-900 dark:text-white flex-1">
                      {scenario.description}
                    </h4>
                  </div>

                  <div className="grid grid-cols-2 gap-3 mb-3">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-medium text-gray-600 dark:text-gray-400">
                        Likelihood:
                      </span>
                      <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                        <div
                          className="bg-blue-600 dark:bg-blue-400 h-2 rounded-full"
                          style={{ width: `${scenario.likelihood * 100}%` }}
                        ></div>
                      </div>
                      <span className="text-xs text-gray-500 dark:text-gray-500">
                        {(scenario.likelihood * 100).toFixed(0)}%
                      </span>
                    </div>

                    <div className="flex items-center gap-2">
                      <span className="text-xs font-medium text-gray-600 dark:text-gray-400">
                        Impact:
                      </span>
                      <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                        <div
                          className="bg-red-600 dark:bg-red-400 h-2 rounded-full"
                          style={{ width: `${scenario.impact * 100}%` }}
                        ></div>
                      </div>
                      <span className="text-xs text-gray-500 dark:text-gray-500">
                        {(scenario.impact * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>

                  <div className="p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
                    <p className="text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Prevention Strategy:
                    </p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {scenario.prevention}
                    </p>
                  </div>
                </Card>
              ))}
            </div>
          </div>
        );
      })}

      {scenarios.length === 0 && (
        <Card className="p-8 text-center">
          <p className="text-gray-500 dark:text-gray-400">
            No failure scenarios identified yet. Run pre-mortem analysis to detect risks.
          </p>
        </Card>
      )}
    </div>
  );
}
