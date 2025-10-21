/**
 * Audit Results Panel
 * Displays theater/production/quality audit results for Loop 3
 *
 * Week 12 Day 1 Implementation
 */

'use client';

interface AuditResults {
  theater: { passed: number; failed: number; total: number };
  production: { passed: number; failed: number; total: number };
  quality: { passed: number; failed: number; total: number };
  overallScore: number;
}

interface AuditResultsPanelProps {
  results: AuditResults;
}

export function AuditResultsPanel({ results }: AuditResultsPanelProps) {
  const stages = [
    {
      name: 'Theater Detection',
      icon: '🎭',
      data: results.theater,
      description: 'Mock code and TODOs removed'
    },
    {
      name: 'Production Testing',
      icon: '⚙️',
      data: results.production,
      description: 'All tests passing in sandbox'
    },
    {
      name: 'Quality Analysis',
      icon: '✅',
      data: results.quality,
      description: 'NASA compliance and code quality'
    }
  ];

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold mb-4">Audit Results</h3>

      <div className="grid grid-cols-3 gap-4 mb-6">
        {stages.map((stage) => (
          <StageCard key={stage.name} stage={stage} />
        ))}
      </div>

      <div className="border-t pt-4">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-gray-700">
            Overall Quality Score
          </span>
          <div className="flex items-center gap-2">
            <div className="w-48 h-2 bg-gray-200 rounded-full overflow-hidden">
              <div
                className={`h-full transition-all duration-500 ${getScoreColor(results.overallScore)}`}
                style={{ width: `${results.overallScore}%` }}
              />
            </div>
            <span className={`text-lg font-bold ${getScoreTextColor(results.overallScore)}`}>
              {results.overallScore}%
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

interface StageData {
  name: string;
  icon: string;
  data: { passed: number; failed: number; total: number };
  description: string;
}

function StageCard({ stage }: { stage: StageData }) {
  const passRate = stage.data.total > 0
    ? (stage.data.passed / stage.data.total) * 100
    : 0;

  return (
    <div className="border rounded-lg p-4">
      <div className="flex items-center gap-2 mb-2">
        <span className="text-2xl">{stage.icon}</span>
        <h4 className="font-medium text-sm">{stage.name}</h4>
      </div>

      <p className="text-xs text-gray-600 mb-3">{stage.description}</p>

      <div className="space-y-1">
        <div className="flex justify-between text-sm">
          <span className="text-green-600">Passed</span>
          <span className="font-medium">{stage.data.passed}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-red-600">Failed</span>
          <span className="font-medium">{stage.data.failed}</span>
        </div>
        <div className="flex justify-between text-sm border-t pt-1">
          <span className="text-gray-700">Total</span>
          <span className="font-medium">{stage.data.total}</span>
        </div>
      </div>

      <div className="mt-3">
        <div className="w-full h-1.5 bg-gray-200 rounded-full overflow-hidden">
          <div
            className={`h-full transition-all duration-500 ${passRate >= 90 ? 'bg-green-500' : passRate >= 70 ? 'bg-yellow-500' : 'bg-red-500'}`}
            style={{ width: `${passRate}%` }}
          />
        </div>
        <p className="text-xs text-right text-gray-500 mt-1">
          {Math.round(passRate)}% pass rate
        </p>
      </div>
    </div>
  );
}

function getScoreColor(score: number): string {
  if (score >= 90) return 'bg-green-500';
  if (score >= 70) return 'bg-yellow-500';
  if (score >= 50) return 'bg-orange-500';
  return 'bg-red-500';
}

function getScoreTextColor(score: number): string {
  if (score >= 90) return 'text-green-600';
  if (score >= 70) return 'text-yellow-600';
  if (score >= 50) return 'text-orange-600';
  return 'text-red-600';
}
