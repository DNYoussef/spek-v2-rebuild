/**
 * tRPC Client-Side Configuration (Atlantis UI)
 *
 * Re-exports backend router and context for Next.js App Router.
 * This file acts as a bridge between frontend and backend.
 *
 * Week 14 Day 1 - Build Fix
 * Version: 8.0.0
 */

// Re-export backend types and router for Next.js
// Using @backend/* path alias defined in tsconfig.json

export { appRouter, type AppRouter } from '@backend/routers';
export { createTRPCContext, type Context } from '@backend/trpc';
