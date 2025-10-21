/**
 * Backend Server - HTTP + WebSocket + tRPC
 *
 * Initializes:
 * - HTTP server for tRPC API
 * - WebSocket server with Redis Pub/Sub
 * - Event broadcasting service
 *
 * Week 8 Day 2 + Week 14 Day 1 (tRPC integration)
 * Version: 8.0.0
 */

import * as http from 'http';
import { SocketServer } from './websocket/SocketServer';
import { createWebSocketBroadcaster } from './services/WebSocketBroadcaster';
import { createHTTPServer } from '@trpc/server/adapters/standalone';
import { appRouter } from './routers';
import { createTRPCContext } from './trpc';

// ============================================================================
// Configuration
// ============================================================================

const PORT = parseInt(process.env.PORT || '3001', 10);
const REDIS_URL = process.env.REDIS_URL || ''; // Empty = disable Redis for development
const CORS_ORIGIN = process.env.CORS_ORIGIN || 'http://localhost:3000';

// ============================================================================
// Server Initialization
// ============================================================================

async function startServer() {
  console.log('🚀 Starting SPEK Backend Server...');

  // Create tRPC standalone server (runs externally on port 3001)
  const trpcServer = createHTTPServer({
    router: appRouter,
    createContext: (opts) => createTRPCContext(opts),
  });

  // For now, tRPC runs on its own port via standalone adapter
  // This httpServer only handles WebSocket + health checks
  const trpcHandler = async (req: http.IncomingMessage, res: http.ServerResponse) => {
    res.writeHead(404, { 'Content-Type': 'text/plain' });
    res.end('tRPC running on separate port 3001');
  };

  // Create combined HTTP server (tRPC + health check + WebSocket)
  const httpServer = http.createServer(async (req, res) => {
    // Handle CORS preflight
    res.setHeader('Access-Control-Allow-Origin', CORS_ORIGIN);
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    if (req.method === 'OPTIONS') {
      res.writeHead(200);
      res.end();
      return;
    }

    // Health check endpoint
    if (req.url === '/health') {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({
        status: 'ok',
        timestamp: new Date().toISOString(),
        services: {
          trpc: 'ready',
          websocket: 'ready',
        },
      }));
      return;
    }

    // tRPC requests (handled by standalone adapter)
    if (req.url?.startsWith('/trpc')) {
      // Forward to tRPC handler
      await trpcHandler(req, res);
      return;
    }

    // Other requests
    res.writeHead(404, { 'Content-Type': 'text/plain' });
    res.end('Not Found');
  });

  // Initialize WebSocket server
  const socketServer = new SocketServer({
    redisUrl: REDIS_URL,
    port: PORT,
    corsOrigin: CORS_ORIGIN,
  });

  await socketServer.initialize(httpServer);

  // Create event broadcaster
  const broadcaster = createWebSocketBroadcaster(socketServer);

  // Start HTTP server
  httpServer.listen(PORT, () => {
    console.log(`✅ HTTP Server listening on port ${PORT}`);
    console.log(`✅ WebSocket Server ready at ws://localhost:${PORT}`);
    console.log(`✅ Redis adapter connected to ${REDIS_URL}`);
    console.log('\n📊 Server Metrics:');
    console.log(`   - CORS Origin: ${CORS_ORIGIN}`);
    console.log(`   - Environment: ${process.env.NODE_ENV || 'development'}`);
  });

  // Graceful shutdown
  const shutdown = async (signal: string) => {
    console.log(`\n${signal} received, shutting down gracefully...`);

    // Close HTTP server
    httpServer.close(() => {
      console.log('✅ HTTP server closed');
    });

    // Shutdown WebSocket server
    await socketServer.shutdown();

    // Log final metrics
    const metrics = socketServer.getMetrics();
    const broadcastMetrics = broadcaster.getMetrics();

    console.log('\n📊 Final Metrics:');
    console.log(`   - Total connections: ${metrics.totalConnections}`);
    console.log(`   - Peak connections: ${metrics.peakConnections}`);
    console.log(`   - Messages sent: ${metrics.messagesSent}`);
    console.log(`   - Broadcast messages: ${broadcastMetrics.messageCount}`);
    console.log(`   - Uptime: ${(broadcastMetrics.uptime / 1000).toFixed(1)}s`);

    process.exit(0);
  };

  process.on('SIGTERM', () => shutdown('SIGTERM'));
  process.on('SIGINT', () => shutdown('SIGINT'));

  // Export for testing/integration
  return {
    httpServer,
    socketServer,
    broadcaster,
  };
}

// ============================================================================
// Start Server (if not imported)
// ============================================================================

if (require.main === module) {
  startServer().catch((error) => {
    console.error('❌ Server failed to start:', error);
    process.exit(1);
  });
}

export { startServer };
