/**
 * tRPC API Route Proxy (DEPRECATED)
 *
 * NOTE: This file is no longer needed since we're using a standalone backend server.
 * The frontend now calls the backend directly via HTTP (http://localhost:3001/trpc).
 *
 * This file is kept for reference but can be deleted.
 *
 * Week 8 Day 1 → Week 14 Day 1 (Standalone Backend)
 * Version: 8.0.0
 */

import { type NextRequest, NextResponse } from 'next/server';

/**
 * Proxy tRPC requests to standalone backend server
 *
 * This is optional - the frontend can call the backend directly.
 * This proxy is only useful if you want all requests to go through Next.js.
 */
const handler = async (req: NextRequest) => {
  const backendUrl = process.env.TRPC_BACKEND_URL || 'http://localhost:3001';
  const path = req.nextUrl.pathname.replace('/api/trpc', '');
  const url = `${backendUrl}/trpc${path}${req.nextUrl.search}`;

  try {
    const response = await fetch(url, {
      method: req.method,
      headers: {
        'Content-Type': 'application/json',
        ...Object.fromEntries(req.headers),
      },
      body: req.method !== 'GET' ? await req.text() : undefined,
    });

    const data = await response.text();

    return new NextResponse(data, {
      status: response.status,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  } catch (error) {
    console.error('tRPC proxy error:', error);
    return new NextResponse('Internal Server Error', { status: 500 });
  }
};

export { handler as GET, handler as POST };
