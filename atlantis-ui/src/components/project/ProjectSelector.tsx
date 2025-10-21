/**
 * Project Selector Component
 *
 * Browse, search, and select from existing SPEK projects.
 * Supports filtering, sorting, and project metadata display.
 *
 * Version: 8.0.0
 * Week: 7 Day 1
 */

'use client';

import { useState } from 'react';
import Link from 'next/link';
import { trpc } from '@/lib/trpc/client';

export interface Project {
  id: string;
  name: string;
  path: string;
  description?: string;
  lastModified: Date;
  status: 'active' | 'completed' | 'archived';
  stats?: {
    totalAgents?: number;
    completedTasks?: number;
    totalTasks?: number;
    qualityScore?: number;
  };
}

export interface ProjectSelectorProps {
  projects?: Project[];
  onProjectSelect?: (project: Project) => void;
  showCreateNew?: boolean;
}

const MOCK_PROJECTS: Project[] = [
  {
    id: '1',
    name: 'spek-v2-rebuild',
    path: 'c:\\Users\\17175\\Desktop\\spek-v2-rebuild',
    description: 'SPEK Platform v2 ground-up rebuild with FSM-first architecture',
    lastModified: new Date('2025-10-08'),
    status: 'active',
    stats: {
      totalAgents: 22,
      completedTasks: 156,
      totalTasks: 200,
      qualityScore: 96
    }
  },
  {
    id: '2',
    name: 'demo-project',
    path: 'c:\\Users\\dev\\demo-project',
    description: 'Demo project for testing SPEK capabilities',
    lastModified: new Date('2025-10-07'),
    status: 'completed',
    stats: {
      totalAgents: 8,
      completedTasks: 45,
      totalTasks: 45,
      qualityScore: 92
    }
  },
  {
    id: '3',
    name: 'legacy-migration',
    path: 'c:\\Users\\dev\\legacy-migration',
    description: 'Legacy codebase migration to modern architecture',
    lastModified: new Date('2025-10-05'),
    status: 'archived',
    stats: {
      totalAgents: 15,
      completedTasks: 89,
      totalTasks: 120,
      qualityScore: 88
    }
  }
];

export function ProjectSelector({
  projects: providedProjects,
  onProjectSelect,
  showCreateNew = true
}: ProjectSelectorProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'active' | 'completed' | 'archived'>('all');
  const [sortBy, setSortBy] = useState<'name' | 'date' | 'quality'>('date');

  // Fetch projects from backend via tRPC
  const { data: apiProjects, isLoading, error } = trpc.project.list.useQuery();

  // Use API projects if available, otherwise fall back to provided projects or mock data
  const projects = apiProjects?.map(p => ({
    ...p,
    lastModified: new Date(p.lastModified),
    stats: {
      totalAgents: 0,
      completedTasks: 0,
      totalTasks: 0,
      qualityScore: 0
    }
  })) || providedProjects || MOCK_PROJECTS;

  const filteredProjects = projects
    .filter(project => {
      const matchesSearch = project.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          project.description?.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesStatus = statusFilter === 'all' || project.status === statusFilter;
      return matchesSearch && matchesStatus;
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.name.localeCompare(b.name);
        case 'date':
          return b.lastModified.getTime() - a.lastModified.getTime();
        case 'quality':
          return (b.stats?.qualityScore || 0) - (a.stats?.qualityScore || 0);
        default:
          return 0;
      }
    });

  const getStatusColor = (status: Project['status']) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'completed':
        return 'bg-blue-100 text-blue-800';
      case 'archived':
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getQualityColor = (score: number) => {
    if (score >= 95) return 'text-green-600';
    if (score >= 90) return 'text-blue-600';
    if (score >= 80) return 'text-yellow-600';
    return 'text-red-600';
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="w-full flex items-center justify-center py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading projects...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="w-full">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <p className="text-red-800 font-medium">Error loading projects</p>
          <p className="text-red-600 text-sm mt-1">{error.message}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full">
      {/* Search and Filters */}
      <div className="mb-6 flex flex-col sm:flex-row gap-4">
        <input
          type="text"
          placeholder="Search projects..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value as typeof statusFilter)}
          className="px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="all">All Status</option>
          <option value="active">Active</option>
          <option value="completed">Completed</option>
          <option value="archived">Archived</option>
        </select>
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value as typeof sortBy)}
          className="px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="date">Sort by Date</option>
          <option value="name">Sort by Name</option>
          <option value="quality">Sort by Quality</option>
        </select>
      </div>

      {/* Create New Project Button */}
      {showCreateNew && (
        <Link
          href="/project/new"
          className="block mb-6 p-6 border-2 border-dashed border-blue-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors text-center"
        >
          <div className="text-blue-600 font-semibold mb-1">+ Create New Project</div>
          <p className="text-sm text-gray-600">Start a fresh SPEK project from scratch</p>
        </Link>
      )}

      {/* Projects List */}
      <div className="space-y-4">
        {filteredProjects.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <p className="text-lg font-medium mb-2">No projects found</p>
            <p className="text-sm">Try adjusting your search or filters</p>
          </div>
        ) : (
          filteredProjects.map((project) => (
            <div
              key={project.id}
              onClick={() => onProjectSelect?.(project)}
              className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow cursor-pointer p-6 border border-gray-200"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-xl font-semibold">{project.name}</h3>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(project.status)}`}>
                      {project.status}
                    </span>
                  </div>
                  {project.description && (
                    <p className="text-sm text-gray-600 mb-2">{project.description}</p>
                  )}
                  <p className="text-xs text-gray-400">{project.path}</p>
                </div>
              </div>

              {/* Project Stats */}
              {project.stats && (
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-4 pt-4 border-t border-gray-100">
                  <div>
                    <p className="text-xs text-gray-500 mb-1">Agents</p>
                    <p className="text-lg font-semibold">{project.stats.totalAgents || 0}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 mb-1">Progress</p>
                    <p className="text-lg font-semibold">
                      {project.stats.totalTasks
                        ? Math.round((project.stats.completedTasks || 0) / project.stats.totalTasks * 100)
                        : 0}%
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 mb-1">Quality</p>
                    <p className={`text-lg font-semibold ${getQualityColor(project.stats.qualityScore || 0)}`}>
                      {project.stats.qualityScore || 0}%
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 mb-1">Last Modified</p>
                    <p className="text-sm font-medium">
                      {project.lastModified.toLocaleDateString()}
                    </p>
                  </div>
                </div>
              )}

              <div className="mt-4 flex gap-2">
                <button className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm font-medium">
                  Open Project
                </button>
                <button className="px-4 py-2 border border-gray-300 rounded hover:bg-gray-50 text-sm font-medium">
                  View Details
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
