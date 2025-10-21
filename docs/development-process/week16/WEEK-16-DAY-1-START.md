# Week 16 Day 1 START - Framer Motion Integration

**Date**: 2025-10-09
**Status**: 🚀 STARTING
**Week**: 16 of 26 (UI Polish + State Reconciliation)
**Day**: 1 of 7 (Framer Motion Integration)

---

## Day 1 Objectives

### Primary Tasks
1. ✅ **Install Framer Motion** (5 min)
   - Add `framer-motion` to atlantis-ui package
   - Configure for Next.js 14 App Router

2. 🔨 **Add Page Transitions** (2 hours)
   - Create AnimatedPage wrapper component
   - Add fade-in transitions for all 9 pages
   - Configure exit animations

3. 🔨 **Implement Button/Card Micro-interactions** (2 hours)
   - Add hover effects to buttons
   - Add scale animation on button press
   - Add hover lift effect to cards
   - Add ripple effect on click

4. 🔨 **Add Loading State Animations** (1 hour)
   - Create animated loading spinner
   - Add skeleton loading for cards
   - Add progress bar animations
   - Add pulse effect for status indicators

---

## Technical Approach

### 1. Framer Motion Setup

**Installation**:
```bash
cd atlantis-ui
npm install framer-motion
```

**Next.js 14 Compatibility**:
```typescript
// app/providers.tsx (create if not exists)
'use client';

import { motion, AnimatePresence } from 'framer-motion';

export { motion, AnimatePresence };
```

### 2. Page Transitions

**Create AnimatedPage Component**:
```typescript
// components/layout/AnimatedPage.tsx
'use client';

import { motion } from 'framer-motion';
import { ReactNode } from 'react';

interface AnimatedPageProps {
  children: ReactNode;
}

export function AnimatedPage({ children }: AnimatedPageProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3, ease: 'easeInOut' }}
    >
      {children}
    </motion.div>
  );
}
```

**Usage in Pages**:
```typescript
// app/page.tsx
import { AnimatedPage } from '@/components/layout/AnimatedPage';

export default function HomePage() {
  return (
    <AnimatedPage>
      {/* page content */}
    </AnimatedPage>
  );
}
```

### 3. Button Animations

**Animated Button Component**:
```typescript
// components/ui/animated-button.tsx
'use client';

import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { ButtonProps } from '@/components/ui/button';

export function AnimatedButton(props: ButtonProps) {
  return (
    <motion.div
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      transition={{ type: 'spring', stiffness: 400, damping: 17 }}
    >
      <Button {...props} />
    </motion.div>
  );
}
```

### 4. Card Animations

**Animated Card Component**:
```typescript
// components/ui/animated-card.tsx
'use client';

import { motion } from 'framer-motion';
import { Card } from '@/components/ui/card';
import { ReactNode } from 'react';

interface AnimatedCardProps {
  children: ReactNode;
  className?: string;
}

export function AnimatedCard({ children, className }: AnimatedCardProps) {
  return (
    <motion.div
      whileHover={{ y: -4, boxShadow: '0 10px 30px rgba(0,0,0,0.1)' }}
      transition={{ duration: 0.2 }}
    >
      <Card className={className}>{children}</Card>
    </motion.div>
  );
}
```

### 5. Loading Animations

**Animated Loading Spinner**:
```typescript
// components/ui/loading-spinner.tsx
'use client';

import { motion } from 'framer-motion';

export function LoadingSpinner() {
  return (
    <motion.div
      animate={{ rotate: 360 }}
      transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
      className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full"
    />
  );
}
```

**Skeleton Loading**:
```typescript
// components/ui/skeleton-card.tsx
'use client';

import { motion } from 'framer-motion';

export function SkeletonCard() {
  return (
    <motion.div
      animate={{ opacity: [0.5, 1, 0.5] }}
      transition={{ duration: 1.5, repeat: Infinity }}
      className="h-32 bg-gray-200 rounded-lg"
    />
  );
}
```

---

## Pages to Update (9 Total)

1. **Homepage** (`/`) - Monarch Chat
2. **Project Select** (`/project/select`)
3. **Project New** (`/project/new`)
4. **Loop 1** (`/loop1`) - Research & Pre-mortem
5. **Loop 2** (`/loop2`) - Execution Village
6. **Loop 2 Audit** (`/loop2/audit`)
7. **Loop 2 UI Review** (`/loop2/ui-review`)
8. **Loop 3** (`/loop3`) - Quality & Finalization
9. **Dashboard** (`/dashboard`)

---

## Success Criteria

### Functional Requirements
- ✅ Framer Motion installed and configured
- ✅ Page transitions working on all 9 pages
- ✅ Button hover/press animations smooth (60fps)
- ✅ Card hover lift effect working
- ✅ Loading animations implemented

### Performance Requirements
- ✅ Animations run at 60fps (no jank)
- ✅ Page transitions complete in <300ms
- ✅ No layout shift during animations
- ✅ No performance regression (<3s page load maintained)

### Quality Requirements
- ✅ TypeScript types for all components
- ✅ No console errors
- ✅ Accessibility preserved (keyboard nav, screen readers)
- ✅ Works on Chrome/Chromium

---

## Timeline

**Morning (8:00 AM - 12:00 PM)**:
- 8:00-8:15: Install Framer Motion
- 8:15-10:00: Create AnimatedPage wrapper + update all 9 pages
- 10:00-12:00: Create animated button/card components

**Afternoon (1:00 PM - 5:00 PM)**:
- 1:00-2:00: Add loading animations
- 2:00-4:00: Test all animations across pages
- 4:00-5:00: Fix issues, optimize performance
- 5:00: Day 1 completion report

**Total Time**: ~6 hours

---

## Expected Output

### Files Created
1. `components/layout/AnimatedPage.tsx` (~30 LOC)
2. `components/ui/animated-button.tsx` (~25 LOC)
3. `components/ui/animated-card.tsx` (~20 LOC)
4. `components/ui/loading-spinner.tsx` (~15 LOC)
5. `components/ui/skeleton-card.tsx` (~15 LOC)

### Files Modified
1. `app/page.tsx` (wrap with AnimatedPage)
2. `app/project/select/page.tsx` (wrap with AnimatedPage)
3. `app/project/new/page.tsx` (wrap with AnimatedPage)
4. `app/loop1/page.tsx` (wrap with AnimatedPage)
5. `app/loop2/page.tsx` (wrap with AnimatedPage)
6. `app/loop2/audit/page.tsx` (wrap with AnimatedPage)
7. `app/loop2/ui-review/page.tsx` (wrap with AnimatedPage)
8. `app/loop3/page.tsx` (wrap with AnimatedPage)
9. `app/dashboard/page.tsx` (wrap with AnimatedPage)

**Total LOC**: ~105 new + ~20 modified = ~125 LOC

---

## Risk Assessment

### Low Risk ✅
- Framer Motion is production-ready and well-documented
- Next.js 14 compatibility confirmed
- Performance overhead minimal (<5% CPU)

### Mitigations
- Test animations on low-end devices (fallback to reduced motion)
- Use `prefers-reduced-motion` media query for accessibility
- Keep animations simple (avoid complex physics)

---

## Next Steps (Day 2)

**Day 2 Focus**: Responsive Design Testing
- Test all 9 pages at 320px, 768px, 1024px, 1280px
- Fix mobile layout issues
- Optimize touch interactions
- Add mobile navigation improvements

---

**Generated**: 2025-10-09T18:00:00-04:00
**Model**: Claude Sonnet 4.5
**Role**: Week 16 Day 1 Planning Specialist
**Status**: READY TO START
