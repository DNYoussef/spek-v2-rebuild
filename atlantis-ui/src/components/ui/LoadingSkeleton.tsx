/**
 * Loading Skeleton Component
 *
 * Animated loading placeholder for content sections.
 *
 * Version: 8.0.0
 * Week: 7 Day 2
 */

export interface LoadingSkeletonProps {
  className?: string;
  variant?: 'text' | 'circular' | 'rectangular';
  width?: string | number;
  height?: string | number;
  count?: number;
}

export function LoadingSkeleton({
  className = '',
  variant = 'rectangular',
  width,
  height,
  count = 1
}: LoadingSkeletonProps) {
  const baseClasses = 'animate-pulse bg-gray-200 dark:bg-gray-700';

  const variantClasses = {
    text: 'h-4 rounded',
    circular: 'rounded-full',
    rectangular: 'rounded-lg'
  };

  const style = {
    width: typeof width === 'number' ? `${width}px` : width,
    height: typeof height === 'number' ? `${height}px` : height
  };

  const skeletonClasses = `${baseClasses} ${variantClasses[variant]} ${className}`;

  if (count === 1) {
    return <div className={skeletonClasses} style={style} />;
  }

  return (
    <div className="space-y-2">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className={skeletonClasses} style={style} />
      ))}
    </div>
  );
}
