/**
 * Research Artifact Display
 * Shows GitHub repositories and academic papers from Loop 1 research phase
 *
 * Week 10 Day 3 Implementation
 */

'use client';

import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';

export interface GitHubRepo {
  name: string;
  url: string;
  stars: number;
  description: string;
}

export interface AcademicPaper {
  title: string;
  authors: string[];
  year: number;
  url: string;
  citations: number;
}

export interface ResearchArtifactDisplayProps {
  githubRepos: GitHubRepo[];
  papers: AcademicPaper[];
  isLoading?: boolean;
}

/**
 * GitHub Repository Card (sub-component)
 */
function GitHubRepoCard({ repo }: { repo: GitHubRepo }) {
  return (
    <div className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:border-blue-500 dark:hover:border-blue-400 transition-colors">
      <div className="flex items-start justify-between mb-2">
        <a
          href={repo.url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-600 dark:text-blue-400 hover:underline font-semibold"
        >
          {repo.name}
        </a>
        <Badge variant="default" className="ml-2">
          ⭐ {repo.stars.toLocaleString()}
        </Badge>
      </div>
      <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-2">
        {repo.description}
      </p>
    </div>
  );
}

/**
 * Academic Paper Card (sub-component)
 */
function AcademicPaperCard({ paper }: { paper: AcademicPaper }) {
  return (
    <div className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:border-blue-500 dark:hover:border-blue-400 transition-colors">
      <a
        href={paper.url}
        target="_blank"
        rel="noopener noreferrer"
        className="text-blue-600 dark:text-blue-400 hover:underline font-semibold block mb-2"
      >
        {paper.title}
      </a>
      <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 mb-2">
        <span>{paper.authors.slice(0, 3).join(', ')}</span>
        {paper.authors.length > 3 && (
          <span>+{paper.authors.length - 3} more</span>
        )}
      </div>
      <div className="flex items-center gap-3 text-xs text-gray-500 dark:text-gray-500">
        <Badge variant="default">{paper.year}</Badge>
        <span>📚 {paper.citations.toLocaleString()} citations</span>
      </div>
    </div>
  );
}

/**
 * Main component (now ≤60 LOC)
 */
export function ResearchArtifactDisplay({
  githubRepos,
  papers,
  isLoading = false,
}: ResearchArtifactDisplayProps) {
  if (isLoading) {
    return (
      <div className="space-y-4">
        <Card className="p-6">
          <div className="animate-pulse space-y-4">
            <div className="h-4 bg-gray-300 dark:bg-gray-700 rounded w-3/4"></div>
            <div className="h-4 bg-gray-300 dark:bg-gray-700 rounded w-1/2"></div>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* GitHub Repositories */}
      <Card className="p-6">
        <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
          GitHub Repositories ({githubRepos.length})
        </h3>
        <div className="space-y-4 max-h-96 overflow-y-auto">
          {githubRepos.length === 0 ? (
            <p className="text-gray-500 dark:text-gray-400 text-sm">No repositories found yet</p>
          ) : (
            githubRepos.map((repo, idx) => <GitHubRepoCard key={idx} repo={repo} />)
          )}
        </div>
      </Card>

      {/* Academic Papers */}
      <Card className="p-6">
        <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
          Academic Papers ({papers.length})
        </h3>
        <div className="space-y-4 max-h-96 overflow-y-auto">
          {papers.length === 0 ? (
            <p className="text-gray-500 dark:text-gray-400 text-sm">No papers found yet</p>
          ) : (
            papers.map((paper, idx) => <AcademicPaperCard key={idx} paper={paper} />)
          )}
        </div>
      </Card>
    </div>
  );
}
