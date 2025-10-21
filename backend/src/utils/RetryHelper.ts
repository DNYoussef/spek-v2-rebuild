/**
 * Retry Helper - Exponential Backoff and Circuit Breaker
 * Provides resilient error handling for external services
 *
 * Week 10 Day 6 Implementation
 */

export interface RetryConfig {
  maxRetries?: number; // Default: 3
  initialDelay?: number; // Default: 1000ms
  maxDelay?: number; // Default: 10000ms
  backoffMultiplier?: number; // Default: 2
  timeout?: number; // Default: 30000ms
}

export interface CircuitBreakerConfig {
  failureThreshold?: number; // Default: 5
  resetTimeout?: number; // Default: 60000ms
}

/**
 * Exponential backoff retry wrapper
 */
export async function withRetry<T>(
  fn: () => Promise<T>,
  config: RetryConfig = {}
): Promise<T> {
  const {
    maxRetries = 3,
    initialDelay = 1000,
    maxDelay = 10000,
    backoffMultiplier = 2,
    timeout = 30000,
  } = config;

  let lastError: Error | null = null;
  let delay = initialDelay;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      // Execute with timeout
      const result = await Promise.race([
        fn(),
        new Promise<T>((_, reject) =>
          setTimeout(() => reject(new Error('Operation timeout')), timeout)
        ),
      ]);

      return result;
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));

      // Don't retry on last attempt
      if (attempt === maxRetries) {
        break;
      }

      // Wait with exponential backoff
      await sleep(Math.min(delay, maxDelay));
      delay *= backoffMultiplier;

      console.log(`Retry attempt ${attempt + 1}/${maxRetries} after ${delay}ms`);
    }
  }

  throw new Error(
    `Failed after ${maxRetries} retries: ${lastError?.message || 'Unknown error'}`
  );
}

/**
 * Circuit breaker pattern
 * Prevents cascading failures by temporarily blocking calls to failing services
 */
export class CircuitBreaker {
  private failureCount = 0;
  private lastFailureTime: number | null = null;
  private state: 'closed' | 'open' | 'half-open' = 'closed';

  constructor(private config: CircuitBreakerConfig = {}) {}

  async execute<T>(fn: () => Promise<T>): Promise<T> {
    const { failureThreshold = 5, resetTimeout = 60000 } = this.config;

    // Check if circuit is open
    if (this.state === 'open') {
      const timeSinceFailure = Date.now() - (this.lastFailureTime || 0);

      if (timeSinceFailure >= resetTimeout) {
        // Try half-open (test if service recovered)
        this.state = 'half-open';
        console.log('Circuit breaker: half-open (testing recovery)');
      } else {
        throw new Error('Circuit breaker open - service unavailable');
      }
    }

    try {
      const result = await fn();

      // Success: reset failure count
      if (this.state === 'half-open') {
        console.log('Circuit breaker: closed (service recovered)');
      }
      this.state = 'closed';
      this.failureCount = 0;
      this.lastFailureTime = null;

      return result;
    } catch (error) {
      this.failureCount++;
      this.lastFailureTime = Date.now();

      if (this.failureCount >= failureThreshold) {
        this.state = 'open';
        console.log(`Circuit breaker: open (${this.failureCount} failures)`);
      }

      throw error;
    }
  }

  getState(): 'closed' | 'open' | 'half-open' {
    return this.state;
  }

  reset(): void {
    this.state = 'closed';
    this.failureCount = 0;
    this.lastFailureTime = null;
  }
}

/**
 * Fallback pattern
 * Provides default value if operation fails
 */
export async function withFallback<T>(
  fn: () => Promise<T>,
  fallbackValue: T
): Promise<T> {
  try {
    return await fn();
  } catch (error) {
    console.warn('Operation failed, using fallback:', error);
    return fallbackValue;
  }
}

/**
 * Rate limiter
 * Prevents overwhelming external services
 */
export class RateLimiter {
  private queue: Array<() => void> = [];
  private activeCount = 0;

  constructor(private maxConcurrent: number = 10) {}

  async execute<T>(fn: () => Promise<T>): Promise<T> {
    // Wait if at capacity
    if (this.activeCount >= this.maxConcurrent) {
      await new Promise<void>((resolve) => this.queue.push(resolve));
    }

    this.activeCount++;

    try {
      return await fn();
    } finally {
      this.activeCount--;

      // Process queue
      const next = this.queue.shift();
      if (next) next();
    }
  }
}

/**
 * Helper: Sleep for ms
 */
function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
