/**
 * Loop 1 Research Agent - GitHub API Integration
 * Searches for similar implementations and academic papers
 *
 * Week 9 - Loop 1 Implementation
 * NASA Compliance: ≤60 LOC per function
 */

import { Octokit } from '@octokit/rest';

export interface ResearchArtifact {
  id: string;
  type: 'github_repo' | 'academic_paper';
  title: string;
  url: string;
  description: string;
  relevanceScore: number;
  metadata: Record<string, unknown>;
}

export interface ResearchResult {
  artifacts: ResearchArtifact[];
  totalFound: number;
  searchQuery: string;
  timestamp: number;
}

export class ResearchAgent {
  private octokit: Octokit;
  private semanticScholarApiKey?: string;

  constructor(githubToken?: string, semanticScholarApiKey?: string) {
    this.octokit = new Octokit({ auth: githubToken });
    this.semanticScholarApiKey = semanticScholarApiKey;
  }

  /**
   * Search GitHub for similar implementations
   * Target: Top 100 results, relevance-scored
   */
  async searchGitHub(query: string, limit = 100): Promise<ResearchArtifact[]> {
    try {
      const response = await this.octokit.rest.search.code({
        q: query,
        per_page: Math.min(limit, 100),
        sort: 'indexed',
      });

      return response.data.items.slice(0, limit).map((item, index) => ({
        id: `github_${item.sha}`,
        type: 'github_repo' as const,
        title: item.name,
        url: item.html_url,
        description: item.repository?.description || '',
        relevanceScore: this.calculateRelevance(item, index, limit),
        metadata: {
          repository: item.repository?.full_name,
          path: item.path,
          sha: item.sha,
        },
      }));
    } catch (error) {
      console.error('GitHub search error:', error);
      return [];
    }
  }

  /**
   * Calculate relevance score (0-1) based on position
   * Higher position = higher relevance
   */
  private calculateRelevance(item: any, index: number, total: number): number {
    const positionScore = 1 - (index / total);
    return Number(positionScore.toFixed(2));
  }

  /**
   * Search academic papers via Semantic Scholar
   * Target: Top 50 papers, relevance-scored
   */
  async searchPapers(query: string, limit = 50): Promise<ResearchArtifact[]> {
    try {
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      };

      if (this.semanticScholarApiKey) {
        headers['x-api-key'] = this.semanticScholarApiKey;
      }

      const response = await fetch(
        `https://api.semanticscholar.org/graph/v1/paper/search?query=${
          encodeURIComponent(query)
        }&limit=${Math.min(limit, 100)}`,
        { headers }
      );

      if (!response.ok) {
        throw new Error(`Semantic Scholar API error: ${response.statusText}`);
      }

      const data = await response.json() as { data?: any[] };
      const papers = data.data || [];

      return papers.slice(0, limit).map((paper: any, index: number) => ({
        id: `paper_${paper.paperId}`,
        type: 'academic_paper' as const,
        title: paper.title,
        url: paper.url || `https://www.semanticscholar.org/paper/${paper.paperId}`,
        description: paper.abstract || '',
        relevanceScore: this.calculateRelevance(paper, index, limit),
        metadata: {
          paperId: paper.paperId,
          year: paper.year,
          citationCount: paper.citationCount,
          authors: paper.authors?.map((a: any) => a.name),
        },
      }));
    } catch (error) {
      console.error('Semantic Scholar search error:', error);
      return [];
    }
  }

  /**
   * Execute full research phase
   * Returns combined GitHub repos + academic papers
   */
  async executeResearch(
    projectDescription: string,
    githubLimit = 100,
    paperLimit = 50
  ): Promise<ResearchResult> {
    const searchQuery = this.generateSearchQuery(projectDescription);

    const [githubResults, paperResults] = await Promise.all([
      this.searchGitHub(searchQuery, githubLimit),
      this.searchPapers(searchQuery, paperLimit),
    ]);

    const artifacts = [...githubResults, ...paperResults].sort(
      (a, b) => b.relevanceScore - a.relevanceScore
    );

    return {
      artifacts,
      totalFound: artifacts.length,
      searchQuery,
      timestamp: Date.now(),
    };
  }

  /**
   * Generate optimized search query from project description
   * Extract key technical terms
   */
  private generateSearchQuery(description: string): string {
    const keywords = description
      .toLowerCase()
      .split(/\s+/)
      .filter(word => word.length > 3)
      .slice(0, 5);

    return keywords.join(' ');
  }
}
