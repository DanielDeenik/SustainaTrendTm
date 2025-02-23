// Frontend configuration
export const config = {
  apiUrl: import.meta.env.VITE_BACKEND_URL || 'http://0.0.0.0:8000',
  development: import.meta.env.DEV || false,
  version: '1.0.0',
  api: {
    metrics: '/api/metrics',
    reports: '/api/reports',
    analyses: '/api/analyses'
  }
};

// Add debug logging for development
if (config.development) {
  console.log('Frontend configuration:', config);
}