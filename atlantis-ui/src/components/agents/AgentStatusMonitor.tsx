/**
 * Agent Status Monitor Component
 *
 * Real-time monitoring of all 22 agents with status indicators.
 *
 * Version: 8.0.0
 * Week: 7 Day 6
 */

'use client';

import { useState, useEffect } from 'react';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { trpc } from '@/lib/trpc/client';
import { useWebSocket } from '@/lib/websocket/WebSocketManager';

interface AgentStatus {
  id: string;
  name: string;
  type: string;
  status: 'idle' | 'active' | 'error';
  cpu?: number;
  memory?: number;
  currentTaskId?: string;
}

export function AgentStatusMonitor() {
  // Fetch initial agent list from backend
  const { data: agentsData, isLoading } = trpc.agent.list.useQuery();

  // Local state for agent status (will be updated via WebSocket)
  const [agents, setAgents] = useState<AgentStatus[]>([]);

  // WebSocket connection for real-time updates
  const { socket, isConnected } = useWebSocket();

  // Initialize agents from API data
  useEffect(() => {
    if (agentsData) {
      setAgents(agentsData.map(agent => ({
        ...agent,
        cpu: Math.floor(Math.random() * 100), // Mock CPU usage
        memory: Math.floor(Math.random() * 512), // Mock memory usage
      })));
    }
  }, [agentsData]);

  // Subscribe to agent status updates via WebSocket
  useEffect(() => {
    if (!socket) return;

    const handleAgentStatus = (data: unknown) => {
      const update = data as { agentId: string; status: 'idle' | 'active' | 'error'; currentTaskId?: string };
      setAgents(prev => prev.map(agent =>
        agent.id === update.agentId
          ? { ...agent, status: update.status, currentTaskId: update.currentTaskId }
          : agent
      ));
    };

    // Subscribe to agent status updates
    socket.on('agent:status', handleAgentStatus);

    return () => {
      socket.off('agent:status', handleAgentStatus);
    };
  }, [socket, agents]);

  if (isLoading) {
    return (
      <Card variant="bordered">
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </Card>
    );
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active':
        return <Badge variant="success" size="sm">Active</Badge>;
      case 'idle':
        return <Badge variant="default" size="sm">Idle</Badge>;
      case 'error':
        return <Badge variant="error" size="sm">Error</Badge>;
      default:
        return <Badge variant="default" size="sm">{status}</Badge>;
    }
  };

  const getTypeBadge = (type: string) => {
    const variants = {
      core: 'info',
      princess: 'warning',
      specialized: 'default'
    } as const;
    return <Badge variant={variants[type as keyof typeof variants] || 'default'} size="sm">{type}</Badge>;
  };

  return (
    <Card variant="bordered">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold">Agent Status Monitor</h2>
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></div>
          <span className="text-sm text-gray-600">{isConnected ? 'Live' : 'Disconnected'}</span>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Agent</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">CPU %</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Memory MB</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {agents.map(agent => (
              <tr key={agent.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 text-sm font-medium text-gray-900">{agent.name}</td>
                <td className="px-4 py-3 text-sm">{getTypeBadge(agent.type)}</td>
                <td className="px-4 py-3 text-sm">{getStatusBadge(agent.status)}</td>
                <td className="px-4 py-3 text-sm text-gray-600">
                  <div className="flex items-center gap-2">
                    <div className="flex-1 bg-gray-200 rounded-full h-2 w-16">
                      <div
                        className={`h-2 rounded-full ${(agent.cpu ?? 0) > 50 ? 'bg-red-500' : 'bg-green-500'}`}
                        style={{ width: `${agent.cpu ?? 0}%` }}
                      ></div>
                    </div>
                    <span>{agent.cpu ?? 0}%</span>
                  </div>
                </td>
                <td className="px-4 py-3 text-sm text-gray-600">{agent.memory}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}
