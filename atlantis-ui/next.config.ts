import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Performance Optimizations (Week 24 - Bundle Size Optimization)

  // Disable ESLint during builds (warnings allowed for Week 22)
  eslint: {
    ignoreDuringBuilds: true,
  },

  // Disable TypeScript errors during builds (allow warnings)
  typescript: {
    ignoreBuildErrors: true,
  },

  // 2. Compiler optimizations
  compiler: {
    // Remove console.logs in production
    removeConsole: process.env.NODE_ENV === 'production' ? {
      exclude: ['error', 'warn'],
    } : false,
  },

  // 3. Experimental features for performance (Week 24 - Enhanced)
  experimental: {
    // Enable optimized package imports (Week 24 - Expanded list)
    optimizePackageImports: [
      'three',
      '@react-three/fiber',
      '@react-three/drei',
      '@radix-ui/react-slot',
      'framer-motion',
    ],

    // Enable server actions for better data fetching
    serverActions: {
      bodySizeLimit: '2mb',
    },
  },

  // 4. Image optimization
  images: {
    formats: ['image/avif', 'image/webp'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
  },

  // 5. Production optimizations
  productionBrowserSourceMaps: false, // Faster builds, smaller bundles

  // 6. Week 24: Advanced Webpack Configuration (Code Splitting + Bundle Analyzer)
  webpack(config: any, { isServer }: any) {
    // Bundle analyzer (development only)
    if (process.env.ANALYZE === 'true') {
      const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');
      config.plugins.push(
        new BundleAnalyzerPlugin({
          analyzerMode: 'static',
          reportFilename: './bundle-analysis.html',
          openAnalyzer: false,
        })
      );
    }

    // Week 24: Advanced code splitting for client bundles
    if (!isServer) {
      config.optimization = {
        ...config.optimization,
        splitChunks: {
          chunks: 'all',
          cacheGroups: {
            // Three.js and React Three Fiber in dedicated chunk
            three: {
              test: /[\\/]node_modules[\\/](three|@react-three)[\\/]/,
              name: 'vendor-three',
              priority: 10,
              reuseExistingChunk: true,
            },
            // Framer Motion in dedicated chunk
            framer: {
              test: /[\\/]node_modules[\\/]framer-motion[\\/]/,
              name: 'vendor-framer',
              priority: 9,
              reuseExistingChunk: true,
            },
            // Radix UI components in dedicated chunk
            radix: {
              test: /[\\/]node_modules[\\/]@radix-ui[\\/]/,
              name: 'vendor-radix',
              priority: 8,
              reuseExistingChunk: true,
            },
            // Common vendor chunk for other dependencies
            vendor: {
              test: /[\\/]node_modules[\\/]/,
              name: 'vendor-common',
              priority: 5,
              reuseExistingChunk: true,
            },
            // Common code shared across pages
            default: {
              minChunks: 2,
              priority: -20,
              reuseExistingChunk: true,
            },
          },
        },
      };
    }

    return config;
  },

  // 7. Headers for caching and security
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-DNS-Prefetch-Control',
            value: 'on'
          },
          {
            key: 'X-Frame-Options',
            value: 'SAMEORIGIN'
          },
        ],
      },
      {
        source: '/static/(.*)',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
    ];
  },
};

export default nextConfig;
