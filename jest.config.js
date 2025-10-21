/** @type {import('jest').Config} */
export default {
  preset: 'ts-jest/presets/default-esm',
  testEnvironment: 'node',
  extensionsToTreatAsEsm: ['.ts'],
  moduleNameMapper: {
    '^(\.{1,2}/.*)\.js$': '$1',
  },
  transform: {
    '^.+\.tsx?$': [
      'ts-jest',
      {
        useESM: true,
      },
    ],
  },
  testMatch: [
    '**/tests/**/*.test.ts',
    '!**/tests/e2e/**',        // Exclude Playwright E2E tests
    '!**/tests/**/*.spec.ts',  // Exclude Playwright spec files  
    '!**/atlantis-ui/tests/**' // Exclude all atlantis-ui tests (use Playwright)
  ],
  collectCoverageFrom: [
    'src/**/*.ts',
    '!src/**/*.d.ts',
    '!src/**/index.ts'
  ],
  coverageThreshold: {
    global: {
      statements: 80,
      branches: 75,
      functions: 80,
      lines: 80
    }
  },
  testTimeout: 10000,
  // Ignore build directories, Playwright tests, and node_modules
  watchPathIgnorePatterns: [
    '<rootDir>/node_modules/',
    '<rootDir>/atlantis-ui/.next/',
    '<rootDir>/atlantis-ui/node_modules/',
    '<rootDir>/atlantis-ui/tests/',  // Ignore Playwright tests
    '<rootDir>/backend/dist/',
    '<rootDir>/backend/node_modules/',
    '<rootDir>/.next/',
    '<rootDir>/dist/',
    '<rootDir>/build/',
    '<rootDir>/coverage/'
  ],
  modulePathIgnorePatterns: [
    '<rootDir>/atlantis-ui/.next/',
    '<rootDir>/atlantis-ui/tests/',  // Ignore Playwright tests
    '<rootDir>/backend/dist/',
    '<rootDir>/dist/',
    '<rootDir>/build/'
  ]
};
