// Frontend configuration
export const config = {
  apiUrl: 'http://0.0.0.0:8000',  // Hardcode for development
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