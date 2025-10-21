/**
 * Monarch Chat Component
 *
 * Interactive chat interface for Queen agent orchestration.
 * Supports real-time message streaming via WebSocket.
 *
 * Version: 8.0.0
 * Week: 7 Day 1
 */

'use client';

import { useState, useRef, useEffect } from 'react';
import { trpc } from '@/lib/trpc/client';
import { useWebSocket } from '@/lib/websocket/WebSocketManager';

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  agentId?: string;
}

export interface MonarchChatProps {
  projectId?: string;
  onMessageSent?: (message: string) => void;
  disabled?: boolean;
}

export function MonarchChat({ projectId, onMessageSent, disabled = false }: MonarchChatProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'system',
      content: 'Welcome to SPEK Atlantis. I\'m the Queen agent, ready to orchestrate your project.',
      timestamp: new Date(),
      agentId: 'queen'
    }
  ]);
  const [input, setInput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { socket } = useWebSocket();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Listen for responses from Claude Code via WebSocket
  useEffect(() => {
    if (!socket) return;

    const handleMonarchMessage = (data: any) => {
      console.log('📨 Received message from Queen:', data);

      const assistantMessage: Message = {
        id: data.taskId || Date.now().toString(),
        role: 'assistant',
        content: data.content,
        timestamp: new Date(data.timestamp || Date.now()),
        agentId: 'queen'
      };

      setMessages(prev => [...prev, assistantMessage]);
      setIsProcessing(false);
    };

    const handleAgentSpawned = (data: any) => {
      console.log('🐝 Agent spawned:', data);

      const spawnMessage: Message = {
        id: `spawn-${Date.now()}`,
        role: 'system',
        content: `🐝 ${data.agentId} has been spawned by ${data.parentAgent} (${data.loop})`,
        timestamp: new Date(data.timestamp),
        agentId: data.agentId
      };

      setMessages(prev => [...prev, spawnMessage]);
    };

    const handleTaskProgress = (data: any) => {
      console.log('📊 Task progress:', data);

      // Update the last message or add a new progress message
      const progressMessage: Message = {
        id: `progress-${data.taskId}-${Date.now()}`,
        role: 'system',
        content: `⏳ ${data.agentId}: ${data.message} (${data.progress}%)`,
        timestamp: new Date(),
        agentId: data.agentId
      };

      setMessages(prev => [...prev, progressMessage]);
    };

    const handleTaskCompleted = (data: any) => {
      console.log('✅ Task completed:', data);

      const completionMessage: Message = {
        id: `complete-${data.taskId}`,
        role: 'system',
        content: `✅ ${data.agentId} completed their task!`,
        timestamp: new Date(data.timestamp),
        agentId: data.agentId
      };

      setMessages(prev => [...prev, completionMessage]);
      setIsProcessing(false);
    };

    const handleAgentError = (data: any) => {
      console.error('❌ Agent error:', data);

      const errorMessage: Message = {
        id: `error-${data.taskId}`,
        role: 'system',
        content: `❌ ${data.agentId} encountered an error: ${data.error}`,
        timestamp: new Date(data.timestamp),
        agentId: data.agentId
      };

      setMessages(prev => [...prev, errorMessage]);
      setIsProcessing(false);
    };

    socket.on('monarch:message', handleMonarchMessage);
    socket.on('agent:spawned', handleAgentSpawned);
    socket.on('task:update', handleTaskProgress);
    socket.on('task:completed', handleTaskCompleted);
    socket.on('agent:error', handleAgentError);

    return () => {
      socket.off('monarch:message', handleMonarchMessage);
      socket.off('agent:spawned', handleAgentSpawned);
      socket.off('task:update', handleTaskProgress);
      socket.off('task:completed', handleTaskCompleted);
      socket.off('agent:error', handleAgentError);
    };
  }, [socket]);

  const handleSend = async () => {
    if (!input.trim() || isProcessing || disabled) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    const messageContent = input.trim();
    setInput('');
    setIsProcessing(true);
    onMessageSent?.(messageContent);

    try {
      // Send to Flask backend at localhost:5000
      const response = await fetch('http://localhost:5000/api/monarch/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: messageContent,
          projectId: projectId
        })
      });

      const data = await response.json();

      if (data.success) {
        const assistantMessage: Message = {
          id: Date.now().toString(),
          role: 'assistant',
          content: data.response,
          timestamp: new Date(),
          agentId: 'queen'
        };
        setMessages(prev => [...prev, assistantMessage]);
      } else {
        throw new Error(data.message || 'Unknown error');
      }
    } catch (error) {
      const errorMessage: Message = {
        id: Date.now().toString(),
        role: 'system',
        content: `Error: ${error instanceof Error ? error.message : 'Failed to send message'}`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-lg px-4 py-3 ${
                message.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : message.role === 'system'
                  ? 'bg-gray-100 text-gray-800 border border-gray-200'
                  : 'bg-white text-gray-900 border border-gray-200'
              }`}
            >
              {message.agentId && message.role !== 'user' && (
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs font-semibold uppercase text-blue-600">
                    {message.agentId}
                  </span>
                  <div className="w-1.5 h-1.5 rounded-full bg-green-500"></div>
                </div>
              )}
              <p className="text-sm whitespace-pre-wrap">{message.content}</p>
              <p className={`text-xs mt-1 ${
                message.role === 'user' ? 'text-blue-100' : 'text-gray-400'
              }`}>
                {message.timestamp.toLocaleTimeString()}
              </p>
            </div>
          </div>
        ))}
        {isProcessing && (
          <div className="flex justify-start">
            <div className="bg-white border border-gray-200 rounded-lg px-4 py-3">
              <div className="flex items-center gap-2">
                <div className="flex gap-1">
                  <div className="w-2 h-2 rounded-full bg-blue-600 animate-bounce" style={{ animationDelay: '0ms' }}></div>
                  <div className="w-2 h-2 rounded-full bg-blue-600 animate-bounce" style={{ animationDelay: '150ms' }}></div>
                  <div className="w-2 h-2 rounded-full bg-blue-600 animate-bounce" style={{ animationDelay: '300ms' }}></div>
                </div>
                <span className="text-xs text-gray-500">Queen is thinking...</span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t p-4 bg-gray-50">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask Monarch to help with your project..."
            className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={disabled || isProcessing}
          />
          <button
            onClick={handleSend}
            disabled={disabled || isProcessing || !input.trim()}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium transition-colors"
          >
            Send
          </button>
        </div>
        {projectId && (
          <p className="text-xs text-gray-500 mt-2">
            Project: <span className="font-medium">{projectId}</span>
          </p>
        )}
      </div>
    </div>
  );
}
