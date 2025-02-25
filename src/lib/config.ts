// Frontend configuration
export const config = {
  apiUrl: '', // Empty base URL to use Vite's proxy
  development: true,
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