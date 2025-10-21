/**
 * Documentation Cleanup UI
 * User approval interface for documentation cleanup actions
 *
 * Week 12 Day 3 Implementation
 * CRITICAL: MANDATORY user approval before any file operations
 */

'use client';

import { useState } from 'react';

interface OutdatedDoc {
  filePath: string;
  reason: string;
  severity: 'low' | 'medium' | 'high';
  suggestedAction: 'archive' | 'update' | 'delete';
}

interface DocumentationCleanupUIProps {
  outdatedDocs: OutdatedDoc[];
  onApprove: (approvedActions: Array<{ filePath: string; action: string }>) => void;
  onCancel: () => void;
}

export function DocumentationCleanupUI({
  outdatedDocs,
  onApprove,
  onCancel
}: DocumentationCleanupUIProps) {
  const [selectedDocs, setSelectedDocs] = useState<Set<string>>(new Set());
  const [actions, setActions] = useState<Record<string, string>>({});

  const toggleDoc = (filePath: string) => {
    const newSelected = new Set(selectedDocs);
    if (newSelected.has(filePath)) {
      newSelected.delete(filePath);
    } else {
      newSelected.add(filePath);
      // Set default action
      const doc = outdatedDocs.find(d => d.filePath === filePath);
      if (doc && !actions[filePath]) {
        setActions({ ...actions, [filePath]: doc.suggestedAction });
      }
    }
    setSelectedDocs(newSelected);
  };

  const setAction = (filePath: string, action: string) => {
    setActions({ ...actions, [filePath]: action });
  };

  const handleApprove = () => {
    const approvedActions = Array.from(selectedDocs).map(filePath => ({
      filePath,
      action: actions[filePath] || 'archive'
    }));
    onApprove(approvedActions);
  };

  const groupedDocs = {
    high: outdatedDocs.filter(d => d.severity === 'high'),
    medium: outdatedDocs.filter(d => d.severity === 'medium'),
    low: outdatedDocs.filter(d => d.severity === 'low')
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 max-w-4xl mx-auto">
      <div className="mb-6">
        <h2 className="text-2xl font-bold mb-2">Documentation Cleanup</h2>
        <p className="text-gray-600">
          {outdatedDocs.length} outdated documentation files found. Review and approve cleanup actions.
        </p>
        <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p className="text-sm text-yellow-800">
            ⚠️ <strong>Important:</strong> Files will be archived to <code>.archive/</code> directory, not deleted.
            You can restore them if needed.
          </p>
        </div>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <SeverityCard
          severity="high"
          count={groupedDocs.high.length}
          color="red"
        />
        <SeverityCard
          severity="medium"
          count={groupedDocs.medium.length}
          color="yellow"
        />
        <SeverityCard
          severity="low"
          count={groupedDocs.low.length}
          color="blue"
        />
      </div>

      {/* File List */}
      <div className="space-y-2 mb-6 max-h-96 overflow-y-auto">
        {outdatedDocs.map((doc) => (
          <DocumentRow
            key={doc.filePath}
            doc={doc}
            selected={selectedDocs.has(doc.filePath)}
            action={actions[doc.filePath]}
            onToggle={() => toggleDoc(doc.filePath)}
            onActionChange={(action) => setAction(doc.filePath, action)}
          />
        ))}
      </div>

      {/* Actions */}
      <div className="flex items-center justify-between pt-4 border-t">
        <div className="text-sm text-gray-600">
          {selectedDocs.size} of {outdatedDocs.length} files selected
        </div>
        <div className="flex gap-3">
          <button
            onClick={onCancel}
            className="px-6 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition"
          >
            Cancel
          </button>
          <button
            onClick={handleApprove}
            disabled={selectedDocs.size === 0}
            className={`
              px-6 py-2 rounded-lg transition
              ${selectedDocs.size > 0
                ? 'bg-blue-600 text-white hover:bg-blue-700'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
              }
            `}
          >
            Approve Cleanup ({selectedDocs.size} files)
          </button>
        </div>
      </div>
    </div>
  );
}

function SeverityCard({
  severity,
  count,
  color
}: {
  severity: string;
  count: number;
  color: string;
}) {
  const colorClasses = {
    red: 'bg-red-50 text-red-700 border-red-200',
    yellow: 'bg-yellow-50 text-yellow-700 border-yellow-200',
    blue: 'bg-blue-50 text-blue-700 border-blue-200'
  };

  return (
    <div className={`p-4 border rounded-lg ${colorClasses[color as keyof typeof colorClasses]}`}>
      <p className="text-sm font-medium uppercase">{severity} Severity</p>
      <p className="text-2xl font-bold mt-1">{count}</p>
    </div>
  );
}

function DocumentRow({
  doc,
  selected,
  action,
  onToggle,
  onActionChange
}: {
  doc: OutdatedDoc;
  selected: boolean;
  action?: string;
  onToggle: () => void;
  onActionChange: (action: string) => void;
}) {
  const severityColors = {
    high: 'text-red-600',
    medium: 'text-yellow-600',
    low: 'text-blue-600'
  };

  return (
    <div className={`
      border rounded-lg p-4 transition
      ${selected ? 'border-blue-500 bg-blue-50' : 'border-gray-200'}
    `}>
      <div className="flex items-start gap-3">
        <input
          type="checkbox"
          checked={selected}
          onChange={onToggle}
          className="mt-1 w-4 h-4 text-blue-600"
        />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <p className="font-mono text-sm truncate">{doc.filePath}</p>
            <span className={`text-xs font-medium ${severityColors[doc.severity]}`}>
              {doc.severity.toUpperCase()}
            </span>
          </div>
          <p className="text-sm text-gray-600 mb-2">{doc.reason}</p>

          {selected && (
            <div className="flex items-center gap-2">
              <label className="text-xs text-gray-500">Action:</label>
              <select
                value={action || doc.suggestedAction}
                onChange={(e) => onActionChange(e.target.value)}
                className="text-xs px-2 py-1 border border-gray-300 rounded"
              >
                <option value="archive">Archive (recommended)</option>
                <option value="update">Update (manual)</option>
                <option value="delete">Delete (use with caution)</option>
              </select>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
