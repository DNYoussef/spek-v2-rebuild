/**
 * Export Options UI
 * Selection interface for GitHub push vs ZIP download
 *
 * Week 12 Day 4 Implementation
 */

'use client';

import { useState } from 'react';

interface ExportConfig {
  method: 'github' | 'zip';
  zipOptions?: {
    includeNodeModules: boolean;
    includeDotFiles: boolean;
  };
}

interface ExportOptionsUIProps {
  githubConfigured: boolean;
  onExport: (config: ExportConfig) => void;
  onCancel: () => void;
}

export function ExportOptionsUI({
  githubConfigured,
  onExport,
  onCancel
}: ExportOptionsUIProps) {
  const [method, setMethod] = useState<'github' | 'zip'>(
    githubConfigured ? 'github' : 'zip'
  );
  const [zipOptions, setZipOptions] = useState({
    includeNodeModules: false,
    includeDotFiles: false
  });

  const handleExport = () => {
    onExport({
      method,
      zipOptions: method === 'zip' ? zipOptions : undefined
    });
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 max-w-2xl mx-auto">
      <div className="mb-6">
        <h2 className="text-2xl font-bold mb-2">Export Project</h2>
        <p className="text-gray-600">
          Choose how you want to export your project
        </p>
      </div>

      <div className="space-y-4 mb-6">
        {/* GitHub Option */}
        <ExportMethodCard
          method="github"
          selected={method === 'github'}
          disabled={!githubConfigured}
          onSelect={() => setMethod('github')}
          icon="📦"
          title="Push to GitHub"
          description="Create repository and push your project to GitHub"
          features={[
            'Automatic repository creation',
            'CI/CD workflow included',
            'Version control enabled',
            'Collaborate with team'
          ]}
        />

        {/* ZIP Option */}
        <ExportMethodCard
          method="zip"
          selected={method === 'zip'}
          onSelect={() => setMethod('zip')}
          icon="🗜️"
          title="Download as ZIP"
          description="Download your project as a compressed ZIP file"
          features={[
            'Instant download',
            'No GitHub account needed',
            'Portable archive',
            'Easy sharing'
          ]}
        />
      </div>

      {/* ZIP Options */}
      {method === 'zip' && (
        <div className="mb-6 p-4 bg-gray-50 rounded-lg">
          <h3 className="font-medium mb-3">ZIP Options</h3>
          <div className="space-y-2">
            <label className="flex items-start gap-3">
              <input
                type="checkbox"
                checked={zipOptions.includeNodeModules}
                onChange={(e) => setZipOptions({
                  ...zipOptions,
                  includeNodeModules: e.target.checked
                })}
                className="mt-1 w-4 h-4 text-blue-600"
              />
              <div>
                <p className="font-medium text-sm">Include node_modules</p>
                <p className="text-xs text-gray-600">
                  Significantly increases ZIP size (not recommended)
                </p>
              </div>
            </label>

            <label className="flex items-start gap-3">
              <input
                type="checkbox"
                checked={zipOptions.includeDotFiles}
                onChange={(e) => setZipOptions({
                  ...zipOptions,
                  includeDotFiles: e.target.checked
                })}
                className="mt-1 w-4 h-4 text-blue-600"
              />
              <div>
                <p className="font-medium text-sm">Include dot files (.env, .git, etc.)</p>
                <p className="text-xs text-gray-600">
                  May include sensitive configuration files
                </p>
              </div>
            </label>
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex items-center justify-between pt-4 border-t">
        <button
          onClick={onCancel}
          className="px-6 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition"
        >
          Cancel
        </button>
        <button
          onClick={handleExport}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
        >
          {method === 'github' ? 'Push to GitHub' : 'Download ZIP'}
        </button>
      </div>
    </div>
  );
}

function ExportMethodCard({
  selected,
  disabled,
  onSelect,
  icon,
  title,
  description,
  features
}: {
  method: string;
  selected: boolean;
  disabled?: boolean;
  onSelect: () => void;
  icon: string;
  title: string;
  description: string;
  features: string[];
}) {
  return (
    <button
      type="button"
      onClick={onSelect}
      disabled={disabled}
      className={`
        w-full p-6 border-2 rounded-lg text-left transition
        ${disabled
          ? 'border-gray-200 bg-gray-50 opacity-50 cursor-not-allowed'
          : selected
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-200 hover:border-gray-300'
        }
      `}
    >
      <div className="flex items-start gap-4">
        <span className="text-4xl">{icon}</span>
        <div className="flex-1">
          <h3 className="text-lg font-bold mb-1">{title}</h3>
          <p className="text-sm text-gray-600 mb-3">{description}</p>
          <ul className="grid grid-cols-2 gap-2">
            {features.map((feature, index) => (
              <li key={index} className="flex items-center gap-2 text-sm">
                <span className="text-green-500">✓</span>
                <span>{feature}</span>
              </li>
            ))}
          </ul>
          {disabled && (
            <p className="mt-3 text-sm text-red-600">
              ⚠️ GitHub not configured. Complete GitHub setup first.
            </p>
          )}
        </div>
      </div>
    </button>
  );
}
