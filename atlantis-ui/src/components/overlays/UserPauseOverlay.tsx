/**
 * User Pause/Inject Overlay
 * Allows users to pause Loop 1 execution and inject custom input
 *
 * Week 10 Day 2 Implementation
 */

'use client';

import { useState } from 'react';
import { Button } from '../ui/Button';
import { Card } from '../ui/Card';

export interface UserPauseOverlayProps {
  isVisible: boolean;
  loopType: 'loop1' | 'loop2';
  currentPhase: string;
  onResume: (userInput?: string) => void;
  onCancel: () => void;
}

export function UserPauseOverlay({
  isVisible,
  loopType,
  currentPhase,
  onResume,
  onCancel,
}: UserPauseOverlayProps) {
  const [userInput, setUserInput] = useState('');

  if (!isVisible) return null;

  const handleSubmit = (): void => {
    onResume(userInput);
    setUserInput('');
  };

  const handleCancel = (): void => {
    setUserInput('');
    onCancel();
  };

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-2xl p-6 bg-white dark:bg-gray-800">
        <div className="mb-4">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            {loopType === 'loop1' ? 'Loop 1' : 'Loop 2'} Paused
          </h2>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Current Phase: <span className="font-semibold">{currentPhase}</span>
          </p>
        </div>

        <div className="mb-6">
          <label htmlFor="user-input" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Optional Input (will be used in next phase)
          </label>
          <textarea
            id="user-input"
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            placeholder="Enter custom instructions, clarifications, or additional context..."
            className="w-full h-40 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg
                     bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                     focus:ring-2 focus:ring-blue-500 focus:border-transparent
                     resize-none"
          />
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
            {userInput.length} characters
          </p>
        </div>

        <div className="flex gap-3">
          <Button
            onClick={handleSubmit}
            className="flex-1 bg-blue-600 hover:bg-blue-700 text-white"
          >
            Resume {userInput ? 'with Input' : ''}
          </Button>
          <Button
            onClick={handleCancel}
            variant="secondary"
            className="flex-1"
          >
            Cancel
          </Button>
        </div>

        <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
          <p className="text-sm text-blue-800 dark:text-blue-200">
            <strong>Tip:</strong> You can provide additional context, override decisions,
            or inject custom instructions that will be incorporated into the next phase.
          </p>
        </div>
      </Card>
    </div>
  );
}
