/**
 * Backend Entry Point
 *
 * Imports and starts the SPEK backend server.
 *
 * Version: 8.0.0
 */

import { startServer } from './server';

startServer().catch((error) => {
  console.error('❌ Server failed to start:', error);
  process.exit(1);
});
