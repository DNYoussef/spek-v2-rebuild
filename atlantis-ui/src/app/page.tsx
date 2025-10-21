/**
 * Home Page - Monarch Chat Interface
 *
 * Main entry point for SPEK Atlantis UI.
 * Provides Monarch chat interface for interactive project management.
 *
 * Version: 8.1.0
 * Week: 25 (Navigation fix + Bee Hive theme)
 */

'use client';

import { useState } from 'react';
import { AnimatedPage } from '@/components/layout/AnimatedPage';
import { RootLayout } from '@/components/layout/RootLayout';
import { MonarchChat } from '@/components/chat/MonarchChat';
import { ProjectDashboard } from '@/components/dashboard/ProjectDashboard';

export default function HomePage() {
  const [projectChoice, setProjectChoice] = useState<'new' | 'existing' | null>(null);
  const [selectedFolder, setSelectedFolder] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);

  const handleFolderSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files && files.length > 0) {
      // Extract folder path from first file
      // webkitRelativePath gives us "folder/subfolder/file.txt"
      const firstFile = files[0];
      const relativePath = firstFile.webkitRelativePath;

      if (relativePath) {
        // Extract root folder name
        const folderName = relativePath.split('/')[0];
        setSelectedFolder(folderName);

        // Build file list for backend (send relative paths only)
        const fileList = Array.from(files).map(file => ({
          path: file.webkitRelativePath,
          name: file.name,
          size: file.size,
          type: file.type
        }));

        // Send to backend for analysis
        // Backend will read files from this client-provided list
        setIsLoading(true);
        try {
          const response = await fetch('http://localhost:5000/api/project/existing', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              folderName: folderName,
              fileList: fileList
            })
          });

          const data = await response.json();
          console.log('Project loaded:', data);
        } catch (error) {
          console.error('Failed to load project:', error);
        } finally {
          setIsLoading(false);
        }
      }
    }
  };

  return (
    <RootLayout>
      <AnimatedPage className="min-h-screen bg-gradient-to-br from-amber-50 via-yellow-50 to-orange-50">
        <div className="container mx-auto px-8 py-8">
          {/* Hero Section */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center gap-3 mb-4">
              <span className="text-6xl">🐝</span>
              <h1 className="text-5xl font-bold bg-gradient-to-r from-amber-600 via-yellow-500 to-orange-600 bg-clip-text text-transparent">
                Welcome to the Hive
              </h1>
              <span className="text-6xl">🍯</span>
            </div>
            <p className="text-xl text-amber-800 max-w-2xl mx-auto">
              AI-Powered Agent Coordination Platform • 22 Specialized Agents • 3-Loop Quality Methodology
            </p>
          </div>

          {/* Project Choice Section */}
          {!projectChoice && (
            <div className="max-w-4xl mx-auto mb-8">
              <div className="bg-white/90 backdrop-blur rounded-2xl shadow-2xl border-2 border-amber-300 p-8">
                <div className="text-center mb-6">
                  <span className="text-4xl mb-2">👑</span>
                  <h2 className="text-3xl font-bold text-amber-900 mb-2">
                    How Can Queen Help You Today?
                  </h2>
                  <p className="text-amber-700">
                    Select an option to begin your journey with our AI agents
                  </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* New Project Button */}
                  <button
                    onClick={() => setProjectChoice('new')}
                    className="group relative overflow-hidden bg-gradient-to-br from-green-100 to-emerald-100 rounded-xl p-8 border-2 border-green-300 hover:border-green-500 transition-all hover:scale-105 shadow-lg text-left"
                  >
                    <div className="relative z-10">
                      <div className="text-5xl mb-4">🌸</div>
                      <h3 className="text-2xl font-bold text-green-900 mb-2">New Project</h3>
                      <p className="text-green-700 mb-4">
                        Start fresh with Loop 1 research, planning, and pre-mortem analysis
                      </p>
                      <div className="flex items-center text-green-600 font-semibold">
                        Let's Begin →
                      </div>
                    </div>
                  </button>

                  {/* Existing Project Button */}
                  <button
                    onClick={() => setProjectChoice('existing')}
                    className="group relative overflow-hidden bg-gradient-to-br from-amber-100 to-orange-100 rounded-xl p-8 border-2 border-amber-300 hover:border-amber-500 transition-all hover:scale-105 shadow-lg text-left"
                  >
                    <div className="relative z-10">
                      <div className="text-5xl mb-4">📁</div>
                      <h3 className="text-2xl font-bold text-amber-900 mb-2">Existing Project</h3>
                      <p className="text-amber-700 mb-4">
                        Load an existing codebase for analysis, refactoring, or enhancement
                      </p>
                      <div className="flex items-center text-amber-600 font-semibold">
                        Select Folder →
                      </div>
                    </div>
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Folder Selection for Existing Project */}
          {projectChoice === 'existing' && (
            <div className="max-w-4xl mx-auto mb-8">
              <div className="bg-white/90 backdrop-blur rounded-2xl shadow-2xl border-2 border-amber-300 p-8">
                <button
                  onClick={() => setProjectChoice(null)}
                  className="mb-4 text-amber-600 hover:text-amber-800 font-semibold flex items-center gap-2"
                >
                  ← Back to Project Selection
                </button>

                <div className="text-center mb-6">
                  <span className="text-4xl mb-2">📂</span>
                  <h2 className="text-3xl font-bold text-amber-900 mb-2">
                    Select Your Project Folder
                  </h2>
                  <p className="text-amber-700">
                    Queen will analyze your codebase and prepare Context DNA
                  </p>
                </div>

                <div className="space-y-4">
                  {/* Folder Input */}
                  <div className="border-2 border-dashed border-amber-300 rounded-xl p-8 text-center hover:border-amber-500 transition-colors bg-amber-50/50">
                    <label htmlFor="folderInput" className="cursor-pointer block">
                      <div className="text-6xl mb-4">📁</div>
                      <p className="text-lg font-semibold text-amber-900 mb-2">
                        Click to Select Project Folder
                      </p>
                      <p className="text-sm text-amber-700">
                        Choose the root directory of your project
                      </p>
                      <input
                        id="folderInput"
                        type="file"
                        /* @ts-ignore - webkitdirectory is non-standard but widely supported */
                        webkitdirectory=""
                        directory=""
                        onChange={handleFolderSelect}
                        className="hidden"
                      />
                    </label>
                  </div>

                  {selectedFolder && (
                    <div className="bg-green-50 border-2 border-green-300 rounded-xl p-6">
                      <div className="flex items-center gap-3">
                        <span className="text-3xl">✅</span>
                        <div className="flex-1">
                          <p className="font-semibold text-green-900">Folder Selected:</p>
                          <p className="text-green-700 font-mono text-sm">{selectedFolder}</p>
                        </div>
                      </div>

                      {isLoading && (
                        <div className="mt-4 text-center">
                          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-600 mx-auto mb-2"></div>
                          <p className="text-amber-800">Queen is analyzing your project...</p>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Chat Interface - Show after project choice */}
          {projectChoice && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Monarch Chat - 2 columns */}
              <div className="lg:col-span-2">
                <div className="bg-white/80 backdrop-blur rounded-2xl shadow-xl border-2 border-amber-200 p-6 min-h-[600px] hover:shadow-2xl transition-shadow">
                  <div className="mb-4">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-3xl">👑</span>
                      <h2 className="text-2xl font-bold text-amber-900">Monarch Chat</h2>
                      <span className="ml-auto px-3 py-1 bg-amber-100 text-amber-800 text-xs font-semibold rounded-full">
                        {projectChoice === 'new' ? '🌸 New Project' : '📁 Existing Project'}
                      </span>
                    </div>
                    <p className="text-sm text-amber-700">
                      Interact with the Queen agent to orchestrate your {projectChoice === 'new' ? 'new' : 'existing'} project
                    </p>
                  </div>

                  {/* Chat Interface (MonarchChat component) */}
                  <MonarchChat />
                </div>
              </div>

              {/* Project Dashboard - 1 column */}
              <div className="lg:col-span-1">
                <div className="bg-white/90 backdrop-blur rounded-2xl shadow-xl border-2 border-amber-200 p-6 hover:shadow-2xl transition-shadow">
                  <div className="flex items-center gap-2 mb-4">
                    <span className="text-2xl">📊</span>
                    <h2 className="text-xl font-bold text-amber-900">Live Dashboard</h2>
                  </div>
                  <ProjectDashboard />
                </div>
              </div>
            </div>
          )}

          {/* Quick Action Cards - Only show if no choice made */}
          {!projectChoice && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
              <a href="/loop1" className="group">
                <div className="bg-gradient-to-br from-green-100 to-emerald-100 rounded-xl p-6 border-2 border-green-300 hover:border-green-500 transition-all hover:scale-105 shadow-lg">
                  <div className="text-4xl mb-2">🌸</div>
                  <h3 className="text-lg font-bold text-green-900 mb-1">Loop 1: Research</h3>
                  <p className="text-sm text-green-700">View research & pre-mortem analysis</p>
                </div>
              </a>

              <a href="/loop2" className="group">
                <div className="bg-gradient-to-br from-amber-100 to-yellow-100 rounded-xl p-6 border-2 border-amber-300 hover:border-amber-500 transition-all hover:scale-105 shadow-lg">
                  <div className="text-4xl mb-2">🐝</div>
                  <h3 className="text-lg font-bold text-amber-900 mb-1">Loop 2: Execution</h3>
                  <p className="text-sm text-amber-700">See Princess Hive in action</p>
                </div>
              </a>

              <a href="/loop3" className="group">
                <div className="bg-gradient-to-br from-orange-100 to-amber-100 rounded-xl p-6 border-2 border-orange-300 hover:border-orange-500 transition-all hover:scale-105 shadow-lg">
                  <div className="text-4xl mb-2">🍯</div>
                  <h3 className="text-lg font-bold text-orange-900 mb-1">Loop 3: Quality</h3>
                  <p className="text-sm text-orange-700">View quality gates & finalization</p>
                </div>
              </a>
            </div>
          )}
        </div>
      </AnimatedPage>
    </RootLayout>
  );
}
