/**
 * GitHub Setup Wizard
 * Form for configuring GitHub repository creation
 *
 * Week 12 Day 2 Implementation
 */

'use client';

import { useState } from 'react';

interface GitHubConfig {
  repoName: string;
  visibility: 'public' | 'private';
  description: string;
  license?: string;
}

interface GitHubSetupWizardProps {
  onSubmit: (config: GitHubConfig) => void;
  onSkip: () => void;
}

const LICENSES = [
  { value: 'mit', label: 'MIT License' },
  { value: 'apache-2.0', label: 'Apache License 2.0' },
  { value: 'gpl-3.0', label: 'GNU GPLv3' },
  { value: 'bsd-3-clause', label: 'BSD 3-Clause' },
  { value: 'unlicense', label: 'The Unlicense' },
  { value: 'none', label: 'No License' }
];

export function GitHubSetupWizard({ onSubmit, onSkip }: GitHubSetupWizardProps) {
  const [config, setConfig] = useState<GitHubConfig>({
    repoName: '',
    visibility: 'private',
    description: '',
    license: 'mit'
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!config.repoName) {
      newErrors.repoName = 'Repository name is required';
    } else if (config.repoName.length > 100) {
      newErrors.repoName = 'Repository name must be ≤100 characters';
    } else if (!/^[a-zA-Z0-9_-]+$/.test(config.repoName)) {
      newErrors.repoName = 'Only alphanumeric, hyphens, and underscores allowed';
    } else if (!/^[a-zA-Z0-9]/.test(config.repoName)) {
      newErrors.repoName = 'Must start with alphanumeric character';
    }

    if (!config.description) {
      newErrors.description = 'Description is required';
    } else if (config.description.length > 350) {
      newErrors.description = 'Description must be ≤350 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validateForm()) {
      onSubmit(config);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 max-w-2xl mx-auto">
      <div className="mb-6">
        <h2 className="text-2xl font-bold mb-2">GitHub Repository Setup</h2>
        <p className="text-gray-600">
          Configure your GitHub repository for this project
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Repository Name */}
        <div>
          <label htmlFor="repoName" className="block text-sm font-medium mb-2">
            Repository Name <span className="text-red-500">*</span>
          </label>
          <input
            id="repoName"
            type="text"
            value={config.repoName}
            onChange={(e) => setConfig({ ...config, repoName: e.target.value })}
            className={`
              w-full px-4 py-2 border rounded-lg
              ${errors.repoName ? 'border-red-500' : 'border-gray-300'}
              focus:outline-none focus:ring-2 focus:ring-blue-500
            `}
            placeholder="my-awesome-project"
          />
          {errors.repoName && (
            <p className="text-sm text-red-500 mt-1">{errors.repoName}</p>
          )}
          <p className="text-xs text-gray-500 mt-1">
            {config.repoName.length}/100 characters
          </p>
        </div>

        {/* Description */}
        <div>
          <label htmlFor="description" className="block text-sm font-medium mb-2">
            Description <span className="text-red-500">*</span>
          </label>
          <textarea
            id="description"
            value={config.description}
            onChange={(e) => setConfig({ ...config, description: e.target.value })}
            className={`
              w-full px-4 py-2 border rounded-lg
              ${errors.description ? 'border-red-500' : 'border-gray-300'}
              focus:outline-none focus:ring-2 focus:ring-blue-500
            `}
            placeholder="A brief description of your project..."
            rows={3}
          />
          {errors.description && (
            <p className="text-sm text-red-500 mt-1">{errors.description}</p>
          )}
          <p className="text-xs text-gray-500 mt-1">
            {config.description.length}/350 characters
          </p>
        </div>

        {/* Visibility */}
        <div>
          <label className="block text-sm font-medium mb-2">
            Visibility <span className="text-red-500">*</span>
          </label>
          <div className="grid grid-cols-2 gap-4">
            <VisibilityOption
              value="private"
              selected={config.visibility === 'private'}
              onSelect={() => setConfig({ ...config, visibility: 'private' })}
              icon="🔒"
              title="Private"
              description="Only you can see this repository"
              recommended
            />
            <VisibilityOption
              value="public"
              selected={config.visibility === 'public'}
              onSelect={() => setConfig({ ...config, visibility: 'public' })}
              icon="🌍"
              title="Public"
              description="Anyone can see this repository"
            />
          </div>
        </div>

        {/* License */}
        <div>
          <label htmlFor="license" className="block text-sm font-medium mb-2">
            License (Optional)
          </label>
          <select
            id="license"
            value={config.license}
            onChange={(e) => setConfig({ ...config, license: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {LICENSES.map((license) => (
              <option key={license.value} value={license.value}>
                {license.label}
              </option>
            ))}
          </select>
        </div>

        {/* Actions */}
        <div className="flex items-center justify-between pt-4 border-t">
          <button
            type="button"
            onClick={onSkip}
            className="px-6 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition"
          >
            Skip (Export as ZIP instead)
          </button>
          <button
            type="submit"
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            Create Repository
          </button>
        </div>
      </form>
    </div>
  );
}

function VisibilityOption({
  selected,
  onSelect,
  icon,
  title,
  description,
  recommended
}: {
  value: string;
  selected: boolean;
  onSelect: () => void;
  icon: string;
  title: string;
  description: string;
  recommended?: boolean;
}) {
  return (
    <button
      type="button"
      onClick={onSelect}
      className={`
        relative p-4 border-2 rounded-lg text-left transition
        ${selected ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'}
      `}
    >
      {recommended && (
        <span className="absolute top-2 right-2 text-xs bg-blue-600 text-white px-2 py-0.5 rounded">
          Recommended
        </span>
      )}
      <div className="flex items-start gap-3">
        <span className="text-2xl">{icon}</span>
        <div>
          <h4 className="font-medium mb-1">{title}</h4>
          <p className="text-sm text-gray-600">{description}</p>
        </div>
      </div>
    </button>
  );
}
