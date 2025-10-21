/**
 * tRPC Server Configuration
 *
 * Core tRPC setup including context, middleware, and procedures.
 * Provides type-safe API foundation for SPEK Platform v2.
 *
 * Week 8 Day 1 + Week 14 Day 2 (Standalone Adapter)
 * Version: 8.0.0
 */

import { initTRPC, TRPCError } from '@trpc/server';
import { CreateHTTPContextOptions } from '@trpc/server/adapters/standalone';
import superjson from 'superjson';
import { ZodError } from 'zod';
import type { IncomingMessage, ServerResponse } from 'http';

// ============================================================================
// Context
// ============================================================================

/**
 * Create tRPC context for each request (Standalone HTTP Server).
 *
 * Includes:
 * - Request/response objects
 * - User session (if authenticated)
 * - Database connections
 */
export async function createTRPCContext(opts: CreateHTTPContextOptions) {
  const { req, res } = opts;

  return {
    req,
    res,
    // TODO: Add session/auth when implemented
    // session: await getServerSession(req, res, authOptions),
  };
}

export type Context = Awaited<ReturnType<typeof createTRPCContext>>;

// ============================================================================
// tRPC Initialization
// ============================================================================

const t = initTRPC.context<Context>().create({
  transformer: superjson,
  errorFormatter({ shape, error }) {
    return {
      ...shape,
      data: {
        ...shape.data,
        zodError:
          error.cause instanceof ZodError ? error.cause.flatten() : null,
      },
    };
  },
});

// ============================================================================
// Base Router & Procedure
// ============================================================================

/**
 * Export router and procedure helpers.
 */
export const createTRPCRouter = t.router;
export const publicProcedure = t.procedure;

// ============================================================================
// Protected Procedure (Optional Auth)
// ============================================================================

/**
 * Protected procedure requiring authentication.
 *
 * Usage:
 * ```ts
 * const protectedRouter = createTRPCRouter({
 *   myProtectedQuery: protectedProcedure.query(() => {
 *     // User is authenticated here
 *   }),
 * });
 * ```
 */
export const protectedProcedure = t.procedure.use(({ ctx, next }) => {
  // TODO: Check if user is authenticated
  // if (!ctx.session || !ctx.session.user) {
  //   throw new TRPCError({ code: 'UNAUTHORIZED' });
  // }

  return next({
    ctx: {
      ...ctx,
      // session: ctx.session,
    },
  });
});
