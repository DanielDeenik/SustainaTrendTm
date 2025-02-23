import '@testing-library/jest-dom/extend-expect';
import { vi, afterEach } from 'vitest';

// Mock the $app/environment module
vi.mock('$app/environment', () => ({
  browser: true,
  dev: true,
  building: false,
}));

// Mock $app/stores
vi.mock('$app/stores', () => ({
  page: {
    subscribe: vi.fn()
  }
}));

// Setup fetch mock
global.fetch = vi.fn();

// Clean up after each test
afterEach(() => {
  vi.clearAllMocks();
});