/**
 * Loop 2 MECE Phase Division Algorithm
 * Mutually Exclusive, Collectively Exhaustive phase breakdown
 *
 * Week 9 - Loop 2 Implementation
 * NASA Compliance: ≤60 LOC per function
 */

export interface Task {
  id: string;
  description: string;
  dependencies: string[]; // Task IDs
  estimatedHours: number;
  agentType: string;
  phase?: number;
}

export interface Phase {
  id: number;
  name: string;
  tasks: Task[];
  dependencies: number[]; // Phase IDs
  estimatedHours: number;
  status: 'pending' | 'in_progress' | 'completed';
}

export interface DependencyGraph {
  nodes: Task[];
  edges: Array<{ from: string; to: string }>;
  phases: Phase[];
}

export class MECEPhaseDivision {
  /**
   * Divide tasks into MECE phases
   * Returns 4-6 phases with topological ordering
   */
  async divideTasks(tasks: Task[]): Promise<DependencyGraph> {
    const sortedTasks = this.topologicalSort(tasks);
    const phases = this.groupIntoPhases(sortedTasks);
    const edges = this.buildDependencyEdges(tasks);

    return {
      nodes: sortedTasks,
      edges,
      phases,
    };
  }

  /**
   * Topological sort using Kahn's algorithm
   * Ensures dependencies execute before dependents
   */
  private topologicalSort(tasks: Task[]): Task[] {
    const inDegree = new Map<string, number>();
    const adjList = new Map<string, string[]>();

    // Initialize
    for (const task of tasks) {
      inDegree.set(task.id, 0);
      adjList.set(task.id, []);
    }

    // Build graph
    for (const task of tasks) {
      for (const dep of task.dependencies) {
        adjList.get(dep)?.push(task.id);
        inDegree.set(task.id, (inDegree.get(task.id) || 0) + 1);
      }
    }

    // Find nodes with no dependencies
    const queue: Task[] = [];
    for (const task of tasks) {
      if (inDegree.get(task.id) === 0) {
        queue.push(task);
      }
    }

    // Sort
    const sorted: Task[] = [];
    while (queue.length > 0) {
      const current = queue.shift()!;
      sorted.push(current);

      for (const neighborId of adjList.get(current.id) || []) {
        const newDegree = (inDegree.get(neighborId) || 0) - 1;
        inDegree.set(neighborId, newDegree);

        if (newDegree === 0) {
          const neighbor = tasks.find(t => t.id === neighborId);
          if (neighbor) queue.push(neighbor);
        }
      }
    }

    return sorted;
  }

  /**
   * Group tasks into 4-6 MECE phases
   * Based on dependency levels and logical grouping
   */
  private groupIntoPhases(sortedTasks: Task[]): Phase[] {
    const targetPhaseCount = 5; // Typical: 4-6 phases
    const levelsMap = this.assignDependencyLevels(sortedTasks);
    const maxLevel = Math.max(...Array.from(levelsMap.values()));

    const phases: Phase[] = [];
    const tasksPerPhase = Math.ceil(sortedTasks.length / targetPhaseCount);

    for (let phaseId = 0; phaseId < targetPhaseCount; phaseId++) {
      const phaseTasks: Task[] = [];
      const startLevel = Math.floor((phaseId / targetPhaseCount) * maxLevel);
      const endLevel = Math.floor(((phaseId + 1) / targetPhaseCount) * maxLevel);

      for (const task of sortedTasks) {
        const level = levelsMap.get(task.id) || 0;
        if (level >= startLevel && level < endLevel && phaseTasks.length < tasksPerPhase) {
          task.phase = phaseId;
          phaseTasks.push(task);
        }
      }

      if (phaseTasks.length > 0) {
        phases.push({
          id: phaseId,
          name: `Phase ${phaseId + 1}`,
          tasks: phaseTasks,
          dependencies: this.calculatePhaseDependencies(phaseId, phases),
          estimatedHours: this.calculatePhaseHours(phaseTasks),
          status: 'pending',
        });
      }
    }

    return phases;
  }

  /**
   * Assign dependency levels to tasks
   * Level 0 = no dependencies, Level N = depends on Level N-1
   */
  private assignDependencyLevels(tasks: Task[]): Map<string, number> {
    const levels = new Map<string, number>();

    for (const task of tasks) {
      if (task.dependencies.length === 0) {
        levels.set(task.id, 0);
      } else {
        const depLevels = task.dependencies.map(dep => levels.get(dep) || 0);
        const maxDepLevel = Math.max(...depLevels);
        levels.set(task.id, maxDepLevel + 1);
      }
    }

    return levels;
  }

  /**
   * Calculate phase dependencies
   * Phase depends on previous phases if tasks have cross-phase dependencies
   */
  private calculatePhaseDependencies(
    currentPhase: number,
    phases: Phase[]
  ): number[] {
    const deps = new Set<number>();

    for (let i = 0; i < currentPhase; i++) {
      deps.add(i);
    }

    return Array.from(deps);
  }

  /**
   * Calculate total estimated hours for phase
   */
  private calculatePhaseHours(tasks: Task[]): number {
    return tasks.reduce((sum, task) => sum + task.estimatedHours, 0);
  }

  /**
   * Build dependency edges for visualization
   */
  private buildDependencyEdges(tasks: Task[]): Array<{ from: string; to: string }> {
    const edges: Array<{ from: string; to: string }> = [];

    for (const task of tasks) {
      for (const dep of task.dependencies) {
        edges.push({ from: dep, to: task.id });
      }
    }

    return edges;
  }

  /**
   * Identify bottleneck tasks
   * Tasks that block ≥3 other tasks
   */
  identifyBottlenecks(tasks: Task[]): string[] {
    const blockCount = new Map<string, number>();

    for (const task of tasks) {
      for (const dep of task.dependencies) {
        blockCount.set(dep, (blockCount.get(dep) || 0) + 1);
      }
    }

    return Array.from(blockCount.entries())
      .filter(([_, count]) => count >= 3)
      .map(([taskId, _]) => taskId);
  }
}
