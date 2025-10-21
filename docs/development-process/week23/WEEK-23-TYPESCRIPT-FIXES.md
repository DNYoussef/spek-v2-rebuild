# Week 23 TypeScript Error Fixes

**Version**: 1.0
**Date**: 2025-10-11
**Status**: 🔄 IN PROGRESS
**Target**: Fix 42 TypeScript errors (4.5 hours)

---

## Error Analysis

Total TypeScript errors: **24 errors** (not 42 as estimated)

### Error Categories
1. **Framer Motion conflicts** (1 error) ✅ FIXED
2. **Pinecone metadata type** (1 error)
3. **Context DNA E2E tests** (6 errors)
4. **Playwright test API** (4 errors)
5. **Backend Loop integration** (12 errors)

---

## Fixes Applied

### 1. Framer Motion Conflicts ✅ FIXED

**File**: `atlantis-ui/src/components/ui/animated-button.tsx:44`

**Error**:
```
Type '{ children: ReactNode; onDrag?: DragEventHandler<HTMLButtonElement> ... }'
is not assignable to type 'Omit<HTMLMotionProps<"button">, "ref">'.
Types of property 'onDrag' are incompatible.
```

**Root Cause**: Framer Motion's `onDrag` conflicts with React's native `onDrag` event

**Fix**:
```typescript
// BEFORE
interface AnimatedButtonProps extends Omit<
  ButtonHTMLAttributes<HTMLButtonElement>,
  'onAnimationStart'
> {

// AFTER
interface AnimatedButtonProps extends Omit<
  ButtonHTMLAttributes<HTMLButtonElement>,
  'onAnimationStart' | 'onDrag' | 'onDragStart' | 'onDragEnd'
> {
```

**Status**: ✅ Fixed

---

### 2. Pinecone Metadata Type

**File**: `atlantis-ui/src/services/vectors/PineconeVectorStore.ts:294`

**Error**:
```
Type 'Record<string, unknown>' is not assignable to type 'Partial<RecordMetadata>'.
'string' index signatures are incompatible.
```

**Root Cause**: Pinecone SDK v3+ has strict metadata typing

**Fix**:
```typescript
// BEFORE
metadata: metadata as Record<string, unknown>,

// AFTER
metadata: metadata as Partial<RecordMetadata>,
```

**Status**: ⏳ Pending

---

### 3. Context DNA E2E Test Errors (6 errors)

**File**: `atlantis-ui/tests/e2e/context-dna-integration.spec.ts`

#### Error 3.1: Missing Export
**Line 10**: `Module has no exported member 'AgentContextIntegration'`

**Fix**: Import from correct module
```typescript
// BEFORE
import { AgentContextIntegration } from '../../src/services/context-dna/AgentContextIntegration';

// AFTER
import { AgentContextIntegration } from '../../src/agents/coordination/AgentMemoryIntegration';
```

#### Error 3.2: Function Signature Mismatch
**Line 22**: `Expected 0 arguments, but got 1`

**Fix**: Use no-arg variant
```typescript
// BEFORE
storage = getContextDNAStorage('./data/context-dna-test-e2e.db');

// AFTER
storage = getContextDNAStorage(); // Uses default path
```

#### Error 3.3-3.6: Invalid Properties
**Lines 149, 154, 270, 275, 276**: Properties don't exist on types

**Fix**: Update to match current API
```typescript
// artifactType doesn't exist - remove it
// success property - use different check
// inheritMemories - use different config structure
// memoriesInherited/conversationsInherited - use result.memories/conversations
```

**Status**: ⏳ Pending (requires API investigation)

---

### 4. Playwright Test API Errors (4 errors)

#### Error 4.1: Unused @ts-expect-error
**File**: `tests/e2e/3d-visualization-advanced.spec.ts:328`

**Fix**: Remove unused directive
```typescript
// BEFORE
// @ts-expect-error
if (performance.memory) {

// AFTER
if (performance.memory) {
```

#### Error 4.2: Locator Signature Mismatch
**File**: `tests/e2e/forms.spec.ts:177`

**Error**: `Expected 1-2 arguments, but got 4`

**Fix**: Use single selector or `or()` method
```typescript
// BEFORE
const successMessage = page.locator(
  'text=/Success|Created|Saved/',
  '[role="status"]',
  '.text-green-500',
  '.text-success'
);

// AFTER
const successMessage = page.locator('text=/Success|Created|Saved/, [role="status"]');
```

#### Error 4.3: Promise Not Awaited
**File**: `tests/e2e/navigation-advanced.spec.ts:342`

**Error**: `Property 'includes' does not exist on type 'Promise<string | null>'`

**Fix**: Await the promise
```typescript
// BEFORE
const purpose = request.headerValue('Purpose');
if (purpose.includes('prefetch')) {

// AFTER
const purpose = await request.headerValue('Purpose');
if (purpose?.includes('prefetch')) {
```

#### Error 4.4: Deprecated API
**File**: `tests/e2e/performance.spec.ts:188,195`

**Error**: `Property 'metrics' does not exist on type 'Page'`

**Root Cause**: `page.metrics()` was removed in Playwright v1.30+

**Fix**: Use Performance API instead
```typescript
// BEFORE
const metrics1 = await page.metrics();

// AFTER
const metrics1 = await page.evaluate(() => ({
  JSHeapUsedSize: (performance as any).memory?.usedJSHeapSize || 0,
  JSHeapTotalSize: (performance as any).memory?.totalJSHeapSize || 0,
}));
```

**Status**: ⏳ Pending

---

### 5. Backend Loop Integration Errors (12 errors)

**File**: `backend/src/services/__tests__/Full-3Loop-Integration.test.ts`

#### Error 5.1-5.2: Loop1Orchestrator Constructor
**Lines 24, 157**: `Expected 3-4 arguments, but got 1`

**Root Cause**: Loop1Orchestrator signature changed

**Fix**: Check current constructor signature and update
```typescript
// Check actual signature in Loop1Orchestrator.ts line 45
// Likely needs: new Loop1Orchestrator(projectId, spec, architecture, ?config)
```

#### Error 5.3-5.5: Missing Methods
**Lines 27, 31, 39, 161**: Properties don't exist
- `start()`
- `completeResearch()`
- `completePremortem()`

**Root Cause**: API refactored, methods renamed or removed

**Fix**: Update to current API
```typescript
// Need to check Loop1Orchestrator for current method names
// Likely renamed to more descriptive names or combined
```

#### Error 5.6-5.12: State Properties Missing
**Lines 56, 85, 109, 110, 190**: Properties don't exist on state objects
- `failureRate` on Loop1State
- `status` on Loop2State
- `github` on Loop3State
- `auditResults` on Loop3State

**Root Cause**: State interfaces changed during refactoring

**Fix**: Check current state definitions and update test assertions
```typescript
// Need to review:
// - src/services/loop1/types.ts (Loop1State)
// - src/services/loop2/types.ts (Loop2State)
// - src/services/loop3/types.ts (Loop3State)
```

**Status**: ⏳ Pending (requires backend code review)

---

## Implementation Plan

### Phase 1: Quick Wins (30 minutes) ✅ 1/5 COMPLETE
1. ✅ Framer Motion conflicts - FIXED
2. ⏳ Pinecone metadata type cast
3. ⏳ Remove unused @ts-expect-error
4. ⏳ Fix Playwright locator signatures
5. ⏳ Fix async/await issues

### Phase 2: Context DNA Tests (1 hour)
1. Fix import paths
2. Update function signatures
3. Remove invalid properties
4. Update to current API

### Phase 3: Backend Integration Tests (2.5 hours)
1. Review Loop1/2/3 Orchestrator APIs
2. Review Loop1/2/3 State interfaces
3. Update test file with correct signatures
4. Update assertions to match state properties

### Phase 4: Validation (30 minutes)
1. Run `npx tsc --noEmit` - verify 0 errors
2. Run tests to verify functionality
3. Update documentation

---

## Files Requiring Changes

### Fixed (1 file) ✅
1. `atlantis-ui/src/components/ui/animated-button.tsx` ✅

### Pending (6 files)
2. `atlantis-ui/src/services/vectors/PineconeVectorStore.ts` (1 error)
3. `atlantis-ui/tests/e2e/3d-visualization-advanced.spec.ts` (1 error)
4. `atlantis-ui/tests/e2e/context-dna-integration.spec.ts` (6 errors)
5. `atlantis-ui/tests/e2e/forms.spec.ts` (1 error)
6. `atlantis-ui/tests/e2e/navigation-advanced.spec.ts` (1 error)
7. `atlantis-ui/tests/e2e/performance.spec.ts` (2 errors)
8. `backend/src/services/__tests__/Full-3Loop-Integration.test.ts` (12 errors)

**Total**: 8 files, 24 errors

---

## Time Tracking

| Phase | Estimated | Actual | Status |
|-------|-----------|--------|--------|
| Analysis | 30 min | 30 min | ✅ Complete |
| Phase 1: Quick Wins | 30 min | 10 min | 🔄 1/5 complete |
| Phase 2: Context DNA | 1 hour | - | ⏳ Pending |
| Phase 3: Backend Tests | 2.5 hours | - | ⏳ Pending |
| Phase 4: Validation | 30 min | - | ⏳ Pending |
| **Total** | **4.5 hours** | **0.67 hours** | **15% complete** |

---

## Next Steps

### Immediate (30 minutes)
1. Fix Pinecone metadata type
2. Fix Playwright API issues (4 errors)
3. Remove unused directive

### Short-term (1 hour)
4. Investigate Context DNA API changes
5. Fix 6 Context DNA test errors

### Medium-term (2.5 hours)
6. Review backend Loop orchestrator APIs
7. Fix 12 backend integration test errors

---

## Success Criteria

- [ ] **Zero TypeScript compilation errors**
- [ ] **All tests pass after fixes**
- [ ] **No `@ts-ignore` or `@ts-expect-error` added**
- [ ] **Strict mode enabled in tsconfig.json**
- [ ] **CI/CD TypeScript check: blocking (not non-blocking)**

---

**Version**: 1.0
**Timestamp**: 2025-10-11T19:00:00Z
**Status**: 🔄 15% COMPLETE (1/24 errors fixed)
**Next**: Fix remaining Phase 1 quick wins (4 errors)
