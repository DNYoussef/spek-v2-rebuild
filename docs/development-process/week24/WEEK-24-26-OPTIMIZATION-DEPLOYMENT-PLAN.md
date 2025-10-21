# Week 24-26: Performance Optimization & Production Deployment Plan

**Date**: 2025-10-11
**Status**: 🚀 ACTIVE - Week 24 Performance Optimization Phase
**Target**: Production-ready Atlantis UI deployment

---

## Executive Summary

**Objective**: Optimize Atlantis UI performance and prepare for production deployment

**Current State**:
- ✅ Atlantis UI build successful (6.0s compile, 13 static pages)
- ✅ Week 23 TypeScript fixes complete (0 E2E test errors)
- ⚠️ Performance issues identified (bundle sizes, page load times)
- ⚠️ 40+ backend integration test errors (OPTIONAL to fix)

**Timeline**: 3 weeks (Weeks 24-26)
**Total Effort**: 15 hours (12.5h without backend fixes)

---

## Week 24: Performance Optimization (4.5 hours)

### Task 1: Bundle Size Optimization (4 hours)

#### Current Bundle Analysis

```
Route Analysis (from npm run build):
├─ /loop3:        281 KB (page) + 458 KB (First Load) = 739 KB ❌ CRITICAL
├─ /loop2:         10 KB (page) + 465 KB (First Load) = 475 KB ⚠️  WARNING
├─ /loop1:       4.96 KB (page) + 460 KB (First Load) = 465 KB ⚠️  WARNING
├─ /             :   0 KB (page) + 177 KB (First Load) = 177 KB ✅ GOOD
├─ /settings     :   0 KB (page) + 177 KB (First Load) = 177 KB ✅ GOOD
└─ Shared chunks:                      150 KB                    ✅ GOOD

Total static assets: 2.2 MB
```

**Issues**:
1. **CRITICAL**: `/loop3` page-specific bundle is **281 KB** (140% over 200 KB target)
2. **WARNING**: Loop1/2/3 routes have 460-465 KB First Load JS
3. Three.js not properly code-split (loaded on all loop pages)

#### Optimization Strategy

**1. Dynamic Imports for 3D Components** (1.5 hours):
- Lazy-load Three.js components with `next/dynamic`
- Use `{ ssr: false }` for client-only 3D rendering
- Add loading skeletons during component load

**Files to Modify**:
- [ ] `atlantis-ui/src/app/loop1/page.tsx` - Dynamic import Loop1FlowerGarden3D
- [ ] `atlantis-ui/src/app/loop2/page.tsx` - Dynamic import Loop2BeehiveVillage3D
- [ ] `atlantis-ui/src/app/loop3/page.tsx` - Dynamic import Loop3HoneycombLayers3D

**Pattern**:
```typescript
// BEFORE (static import):
import { Loop3HoneycombLayers3D } from '@/components/three/Loop3HoneycombLayers3D';

// AFTER (dynamic import):
const Loop3HoneycombLayers3D = dynamic(
  () => import('@/components/three/Loop3HoneycombLayers3D').then(mod => mod.Loop3HoneycombLayers3D),
  {
    ssr: false,
    loading: () => <LoadingSkeleton type="3d-visualization" />
  }
);
```

**Expected Impact**: Reduce loop3 bundle from 281 KB → <100 KB (64% reduction)

---

**2. Tree-Shaking Optimization** (1 hour):
- Configure `next.config.ts` for better tree-shaking
- Use named imports instead of default imports
- Remove unused Three.js utilities

**next.config.ts Changes**:
```typescript
experimental: {
  optimizePackageImports: [
    'three',           // ✅ Already added
    '@react-three/fiber',
    '@react-three/drei',
    '@radix-ui/react-slot',  // ✅ Already added
  ],
},

// Add modularizeImports for better tree-shaking
modularizeImports: {
  'three': {
    transform: 'three/{{member}}',
  },
},
```

**Expected Impact**: Reduce shared chunks from 150 KB → ~120 KB (20% reduction)

---

**3. Code Splitting for Heavy Libraries** (1 hour):
- Split Framer Motion animations into separate chunks
- Lazy-load chart libraries (if used in dashboard)
- Defer non-critical JavaScript

**next.config.ts Webpack Config**:
```typescript
webpack(config: any, { isServer }: any) {
  if (!isServer) {
    config.optimization.splitChunks = {
      chunks: 'all',
      cacheGroups: {
        three: {
          test: /[\\/]node_modules[\\/](three|@react-three)[\\/]/,
          name: 'vendor-three',
          priority: 10,
        },
        framer: {
          test: /[\\/]node_modules[\\/]framer-motion[\\/]/,
          name: 'vendor-framer',
          priority: 9,
        },
        default: {
          minChunks: 2,
          priority: -20,
          reuseExistingChunk: true,
        },
      },
    };
  }
  return config;
}
```

**Expected Impact**: Better caching, reduced redundant code

---

**4. Bundle Analysis & Validation** (30 minutes):
```bash
# Run bundle analyzer
ANALYZE=true npm run build

# Open bundle-analysis.html
# Validate:
# - Loop3 page bundle <200 KB
# - Three.js in separate chunk
# - Framer Motion in separate chunk
```

**Success Criteria**:
- [ ] Loop3 page bundle <200 KB (currently 281 KB)
- [ ] Loop1/2 page bundles <50 KB each
- [ ] Three.js in dedicated vendor chunk
- [ ] All routes First Load JS <300 KB

---

### Task 2: Page Load Optimization (30 minutes)

**Current Performance** (estimated):
- Homepage: ~2.5s (slower than target)
- Loop pages: ~4-5s (heavy 3D initialization)

**Optimizations**:

**1. Add Resource Hints** (10 minutes):
```typescript
// atlantis-ui/src/app/layout.tsx
export const metadata = {
  // ... existing metadata
  other: {
    'dns-prefetch': [
      'https://fonts.googleapis.com',
      'https://cdn.jsdelivr.net',
    ],
    'preconnect': [
      { href: 'https://fonts.gstatic.com', crossOrigin: 'anonymous' },
    ],
  },
};
```

**2. Image Optimization** (10 minutes):
- Ensure all images use Next.js `<Image />` component
- Add `priority` prop to above-the-fold images
- Use `placeholder="blur"` for better perceived performance

**3. Font Loading Strategy** (10 minutes):
```typescript
// Use next/font for optimized font loading
import { Inter } from 'next/font/google';

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',  // FOUT instead of FOIT
  variable: '--font-inter',
});
```

**Success Criteria**:
- [ ] Homepage loads <2s (Lighthouse test)
- [ ] Loop pages load <3s
- [ ] Largest Contentful Paint (LCP) <2.5s
- [ ] First Input Delay (FID) <100ms

---

### Task 3: ESLint Warnings Cleanup (30 minutes)

**Current Warnings**: 7 warnings (unused imports, `any` types)

**Fix Strategy**:
```bash
# 1. List all warnings
cd atlantis-ui && npx eslint . --ext .ts,.tsx --max-warnings 0 --format compact

# 2. Auto-fix safe issues
npx eslint . --ext .ts,.tsx --fix

# 3. Manual review remaining warnings
# - Remove unused imports
# - Replace `any` with proper types
```

**Success Criteria**:
- [ ] 0 ESLint warnings
- [ ] All `any` types replaced with proper types (or `unknown` with type guards)

---

## Week 25: Deployment Preparation (6 hours)

### Task 1: Environment Configuration (2 hours)

**Create `.env.example`**:
```env
# Required - Database
DATABASE_URL=postgresql://user:pass@localhost:5432/spek
REDIS_URL=redis://localhost:6379

# Required - APIs
OPENAI_API_KEY=sk-...
PINECONE_API_KEY=...
NEXT_PUBLIC_TRPC_URL=http://localhost:3000/api/trpc

# Optional - Features
NEXT_PUBLIC_ENABLE_3D=true
NEXT_PUBLIC_ENABLE_ANALYTICS=false

# Optional - Performance
NEXT_PUBLIC_MAX_BUNDLE_SIZE=200
```

**Create deployment checklist**:
- [ ] All env vars documented
- [ ] Production values configured (not defaults)
- [ ] Secrets rotated (API keys)
- [ ] Database connection validated

---

### Task 2: Database Migration Scripts (2 hours)

**Create migration infrastructure**:
```bash
# atlantis-ui/prisma/migrations/
├── 001_initial_schema.sql
├── 002_add_context_dna.sql
├── 003_add_agent_logs.sql
└── rollback/
    ├── 001_rollback.sql
    ├── 002_rollback.sql
    └── 003_rollback.sql
```

**Migration script template**:
```sql
-- 001_initial_schema.sql
BEGIN;

CREATE TABLE projects (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_projects_created_at ON projects(created_at);

COMMIT;
```

**Rollback template**:
```sql
-- rollback/001_rollback.sql
BEGIN;

DROP TABLE IF EXISTS projects CASCADE;

COMMIT;
```

---

### Task 3: Rollback Procedures (2 hours)

**Create `docs/ROLLBACK-PROCEDURE.md`**:
```markdown
# Production Rollback Procedure

## When to Rollback
- Error rate >5% sustained for >5 minutes
- Critical data corruption detected
- Security breach confirmed
- Performance degradation >50%

## Rollback Steps

### 1. Stop Traffic (30 seconds)
\`\`\`bash
# Redirect to maintenance page
vercel --prod --env MAINTENANCE_MODE=true
\`\`\`

### 2. Restore Previous Version (2 minutes)
\`\`\`bash
# Vercel rollback
vercel rollback --prod

# OR manual deploy previous commit
git checkout <previous-commit>
vercel --prod
\`\`\`

### 3. Database Rollback (if needed) (5 minutes)
\`\`\`bash
# Run rollback migration
psql $DATABASE_URL < prisma/migrations/rollback/003_rollback.sql
\`\`\`

### 4. Verify Rollback (2 minutes)
\`\`\`bash
# Check health
curl https://spek-v2.vercel.app/api/health

# Check metrics
# - Error rate <1%
# - Response time <200ms
\`\`\`

### 5. Resume Traffic (30 seconds)
\`\`\`bash
vercel --prod --env MAINTENANCE_MODE=false
\`\`\`

## Post-Rollback Actions
- [ ] Document root cause
- [ ] Create GitHub issue
- [ ] Schedule post-mortem
```

---

## Week 26: Production Deployment (2 hours)

### Task 1: Monitoring & Alerting (1 hour)

**Vercel Analytics Setup**:
```typescript
// atlantis-ui/src/app/layout.tsx
import { Analytics } from '@vercel/analytics/react';
import { SpeedInsights } from '@vercel/speed-insights/next';

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        {children}
        <Analytics />
        <SpeedInsights />
      </body>
    </html>
  );
}
```

**Health Check Endpoint**:
```typescript
// atlantis-ui/src/app/api/health/route.ts
export async function GET() {
  return Response.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    version: process.env.VERCEL_GIT_COMMIT_SHA || 'local',
  });
}
```

---

### Task 2: Production Deployment (1 hour)

**Pre-Flight Checklist**:
- [ ] All environment variables configured
- [ ] Database migrations tested
- [ ] Rollback procedure validated
- [ ] Health check endpoint working
- [ ] Analytics/monitoring enabled
- [ ] Performance targets met (bundle <200KB, load <2s)
- [ ] E2E tests passing (139 tests)
- [ ] TypeScript compilation: 0 errors
- [ ] ESLint warnings: 0

**Deployment Commands**:
```bash
# 1. Final build verification
cd atlantis-ui && npm run build

# 2. Deploy to Vercel production
vercel --prod

# 3. Run smoke tests
curl https://spek-v2.vercel.app/api/health
curl https://spek-v2.vercel.app/

# 4. Monitor for 1 hour
# - Error rate <1%
# - Response time <200ms
# - 3D visualization loading correctly
```

**GO/NO-GO Criteria**:
- ✅ **GO**: All performance targets met, 0 critical errors
- ❌ **NO-GO**: Any performance target missed OR critical error >1%

---

## Week 24 Optional: Backend Integration Test Fixes (2.5 hours)

**Files with Errors**:
1. `backend/src/services/__tests__/Full-3Loop-Integration.test.ts` (12 errors)
2. `backend/src/services/__tests__/Loop1-Loop2-Integration.test.ts` (18 errors)

**Error Categories**:
- Constructor signature mismatches (Expected 3-4 args, got 1)
- Missing properties on state objects (`failureRate`, `status`, `github`)
- Method name changes (`start`, `completeResearch`, `completePremortem`)
- Type mismatches (DependencyGraph, Task properties)

**Fix Strategy**:
```typescript
// Update constructor calls
// BEFORE:
const loop1 = new Loop1Orchestrator(projectId);

// AFTER:
const loop1 = new Loop1Orchestrator(
  projectId,
  getContextDNAStorage(),
  getAgentContextManager()
);

// Update method calls
// BEFORE:
await loop1.start();
await loop1.completeResearch();

// AFTER:
await loop1.initialize();
await loop1.submitResearchResults();

// Fix property access
// BEFORE:
const failureRate = state.failureRate;

// AFTER:
const failureRate = state.iterations[0]?.failureRate || 0;
```

**Success Criteria**:
- [ ] 0 TypeScript errors in backend integration tests
- [ ] All integration tests passing

---

## Success Metrics

### Performance Targets

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| **Bundle Size** | <200 KB/route | 281 KB (Loop3) | ❌ TO FIX |
| **Page Load** | <2s homepage | ~2.5s | ⚠️ TO FIX |
| **Page Load** | <3s loop pages | ~4-5s | ⚠️ TO FIX |
| **3D Rendering** | 60 FPS desktop | Unknown | ⚠️ TO TEST |
| **E2E Tests** | 100% passing | 100% (139 tests) | ✅ DONE |
| **TypeScript Errors** | 0 (frontend) | 0 | ✅ DONE |
| **ESLint Warnings** | 0 | 7 | ⚠️ TO FIX |

### Deployment Targets

| Milestone | Target | Status |
|-----------|--------|--------|
| Environment config | 100% documented | ⏳ PENDING |
| Database migrations | Scripts + rollback | ⏳ PENDING |
| Rollback procedure | Documented + tested | ⏳ PENDING |
| Monitoring setup | Analytics + health checks | ⏳ PENDING |
| Production deployment | Successful + stable 1h | ⏳ PENDING |

---

## Risk Assessment

### High Priority Risks

**Risk #1: Bundle size optimization fails**
- **Impact**: Production deployment blocked
- **Probability**: LOW (15%) - Dynamic imports are proven pattern
- **Mitigation**: Have 2D fallback ready (no Three.js required)

**Risk #2: Page load optimization insufficient**
- **Impact**: UX degraded, but deployment can proceed
- **Probability**: MEDIUM (30%) - Heavy 3D content
- **Mitigation**: Progressive enhancement (show 2D first, load 3D async)

**Risk #3: Deployment issues**
- **Impact**: Rollback required
- **Probability**: MEDIUM (25%) - First production deployment
- **Mitigation**: Rollback procedure documented + tested

### Medium Priority Risks

**Risk #4: Backend test fixes take longer than estimated**
- **Impact**: Timeline extends by 1-2 hours
- **Probability**: MEDIUM (40%) - 40+ errors to fix
- **Mitigation**: Mark as OPTIONAL, can defer to post-launch

**Risk #5: Monitoring/alerting setup issues**
- **Impact**: Limited visibility post-launch
- **Probability**: LOW (10%) - Vercel provides built-in tools
- **Mitigation**: Start with Vercel Analytics (free tier)

---

## Timeline & Effort

| Week | Phase | Tasks | Effort | Status |
|------|-------|-------|--------|--------|
| **24** | Performance | Bundle size, page load, ESLint | 4.5h | 🟡 IN PROGRESS |
| **24** | Optional | Backend test fixes | 2.5h | ⬜ PENDING |
| **25** | Deployment Prep | Env config, migrations, rollback | 6h | ⬜ PENDING |
| **26** | Launch | Monitoring, deployment | 2h | ⬜ PENDING |
| **TOTAL** | | | **15h** (12.5h without backend) | **0% COMPLETE** |

---

## Next Steps (Immediate Actions)

### Day 1: Bundle Size Optimization (4 hours)
1. **Create dynamic imports** for Loop1/2/3 3D components (1.5h)
2. **Configure tree-shaking** in next.config.ts (1h)
3. **Setup code splitting** for heavy libraries (1h)
4. **Run bundle analyzer** and validate (30min)

### Day 2: Page Load + ESLint (1 hour)
1. **Add resource hints** (dns-prefetch, preconnect) (10min)
2. **Optimize images** (Next.js Image component) (10min)
3. **Configure font loading** (next/font) (10min)
4. **Fix ESLint warnings** (auto-fix + manual) (30min)

### Day 3-5: Deployment Preparation (6 hours)
1. **Environment configuration** documentation (2h)
2. **Database migration scripts** + rollback (2h)
3. **Rollback procedures** documentation + testing (2h)

### Day 6: Production Deployment (2 hours)
1. **Monitoring & alerting** setup (Vercel Analytics) (1h)
2. **Production deployment** + 1-hour monitoring (1h)

---

**Status**: ✅ PLAN APPROVED - Ready to execute Week 24 optimizations
**Next**: Begin Task 1 - Dynamic imports for 3D components

---

**Generated**: 2025-10-11
**Model**: Claude Sonnet 4.5
**Confidence**: 95% - All tasks well-scoped, proven patterns, realistic effort estimates
